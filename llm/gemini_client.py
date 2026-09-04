from __future__ import annotations
import json
from typing import Any, Dict, Optional
from google import genai
from google.genai import types


class GeminiResearchClient:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is missing. Add it to Streamlit Secrets.")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def research(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config_kwargs: Dict[str, Any] = {
            "tools": [types.Tool(google_search=types.GoogleSearch())],
        }
        if schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = schema
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        if schema:
            try:
                return json.loads(text)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Gemini returned invalid JSON: {exc}") from exc
        return {"text": text, "raw": response}
