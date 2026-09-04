from __future__ import annotations
import json
import re
from typing import Any, Dict, Optional
from google import genai
from google.genai import types


class GeminiResearchClient:
    """Gemini reasoning layer.

    Important: this client deliberately does NOT enable Gemini Google Search.
    Live retrieval is handled by Tavily and its results are passed into Gemini.
    """

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is missing. Add it to Streamlit Secrets.")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        cleaned = (text or "").strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            value = json.loads(cleaned)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            pass
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                value = json.loads(cleaned[start : end + 1])
                if isinstance(value, dict):
                    return value
            except json.JSONDecodeError:
                pass
        raise RuntimeError("Gemini returned invalid JSON. Please run the research again.")

    def research(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if schema:
            prompt += "\n\nReturn ONLY valid JSON. No markdown fences. No commentary outside the JSON object."
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=12000,
                ),
            )
        except Exception as exc:
            message = str(exc)
            if "429" in message or "RESOURCE_EXHAUSTED" in message:
                raise RuntimeError(
                    "Gemini quota/rate limit reached. The app now uses Tavily for live search; "
                    "check the Gemini project quota or switch GEMINI_MODEL to gemini-2.5-flash-lite."
                ) from exc
            raise

        text = (getattr(response, "text", None) or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        if not schema:
            return {"text": text}
        return self._extract_json(text)
