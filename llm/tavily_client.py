from __future__ import annotations
import requests
from typing import Any


class TavilyResearchClient:
    """Tavily retrieval layer with optional deeper page extraction."""

    BASE_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: str):
        if not api_key:
            raise RuntimeError("TAVILY_API_KEY is missing. Add it to Streamlit Secrets.")
        self.api_key = api_key

    def search(
        self,
        query: str,
        *,
        max_results: int = 6,
        topic: str = "general",
        time_range: str | None = None,
        include_domains: list[str] | None = None,
        search_depth: str = "basic",
        include_raw_content: bool = False,
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "query": query,
            "search_depth": search_depth,
            "max_results": max(1, min(int(max_results), 10)),
            "topic": topic,
            "include_answer": False,
            "include_raw_content": include_raw_content,
            "include_images": False,
        }
        if time_range:
            payload["time_range"] = time_range
        if include_domains:
            payload["include_domains"] = include_domains

        try:
            r = requests.post(
                self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=45,
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Tavily connection failed: {exc}") from exc

        if r.status_code != 200:
            try:
                detail = r.json()
            except Exception:
                detail = r.text[:500]
            raise RuntimeError(f"Tavily error {r.status_code}: {detail}")

        data = r.json()
        return data.get("results") or []

    def search_many(self, searches: list[dict[str, Any]]) -> list[dict[str, Any]]:
        combined: list[dict[str, Any]] = []
        seen: set[str] = set()
        for spec in searches:
            results = self.search(**spec)
            for item in results:
                url = item.get("url") or ""
                key = url or f"{item.get('title','')}|{item.get('content','')}"
                if key in seen:
                    continue
                seen.add(key)
                combined.append(item)
        return combined


def format_results(results: list[dict[str, Any]], limit: int = 30) -> str:
    """Give Gemini both search snippets and, when available, extracted page text."""
    lines: list[str] = []
    for i, r in enumerate(results[:limit], 1):
        title = r.get("title") or "Untitled"
        url = r.get("url") or ""
        content = (r.get("content") or "").replace("\n", " ").strip()
        raw = (r.get("raw_content") or "").replace("\n", " ").strip()
        # Keep prompts bounded while preserving much more evidence than a basic snippet.
        if raw:
            raw = raw[:9000]
        score = r.get("score")
        lines.append(
            f"[{i}] {title}\nURL: {url}\nScore: {score}\nSnippet: {content}\n"
            + (f"Page text: {raw}" if raw else "")
        )
    return "\n\n".join(lines)
