from __future__ import annotations
import json
import re
from typing import Any, Dict, Optional
from google import genai
from google.genai import types


class GeminiResearchClient:
    """Gemini-only external research interface using Google Search grounding.

    Structured-output schemas are intentionally not sent to Gemini. Gemini's
    API rejects JSON Schema's `additionalProperties` keyword, and the research
    agents contain flexible evidence objects. We instead request JSON in the
    prompt and parse/validate it locally, which keeps Google Search grounding
    enabled and avoids schema incompatibilities.
    """

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is missing. Add it to Streamlit Secrets.")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    @staticmethod
    def _sources(response) -> list[dict]:
        out = []
        gm = getattr(response, "grounding_metadata", None)
        chunks = getattr(gm, "grounding_chunks", None) if gm else None
        if chunks:
            for ch in chunks:
                web = getattr(ch, "web", None)
                if not web:
                    continue
                uri = getattr(web, "uri", None)
                title = getattr(web, "title", None)
                if uri and not any(x.get("url") == uri for x in out):
                    out.append({"title": title or "Web source", "url": uri, "source_type": "web"})
        return out

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        """Parse JSON returned as raw JSON or inside a markdown code fence."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            value = json.loads(cleaned)
            if isinstance(value, dict):
                return value
            raise RuntimeError("Gemini returned JSON, but the top-level value was not an object.")
        except json.JSONDecodeError:
            # Some responses may contain a small amount of text before/after JSON.
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start >= 0 and end > start:
                try:
                    value = json.loads(cleaned[start:end + 1])
                    if isinstance(value, dict):
                        return value
                except json.JSONDecodeError:
                    pass
            raise RuntimeError("Gemini returned invalid JSON. Re-run the research cycle.")

    def research(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Do not pass response_schema/response_mime_type. The Gemini API does
        # not support `additionalProperties` in its JSON Schema implementation.
        grounded_prompt = prompt
        if schema:
            grounded_prompt += "\n\nReturn ONLY valid JSON. Do not use markdown fences or explanatory text."

        response = self.client.models.generate_content(
            model=self.model,
            contents=grounded_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        text = (getattr(response, "text", None) or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        grounded = self._sources(response)
        if not schema:
            return {"text": text, "sources": grounded}

        data = self._extract_json(text)
        existing = data.get("sources") if isinstance(data, dict) else None
        if isinstance(existing, list):
            seen = {s.get("url") for s in existing if isinstance(s, dict)}
            for s in grounded:
                if s["url"] not in seen:
                    existing.append(s)
        elif isinstance(data, dict):
            data["sources"] = grounded
        return data
