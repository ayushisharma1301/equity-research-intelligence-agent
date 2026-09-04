from __future__ import annotations
import requests
from typing import Any


class TavilyResearchClient:
    """Small Tavily REST client for live web retrieval.

    Tavily is the retrieval layer; Gemini is the reasoning layer. This keeps
    Google Search grounding out of Gemini so the app is not dependent on the
    Gemini Search-grounding quota.
    """

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
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "query": query,
            "search_depth": "basic",
            "max_results": max(1, min(int(max_results), 10)),
            "topic": topic,
            "include_answer": False,
            "include_raw_content": False,
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
                timeout=35,
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
        """Run a small, deliberate set of searches and deduplicate URLs."""
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
    """Compact, citation-friendly text for Gemini prompts."""
    lines: list[str] = []
    for i, r in enumerate(results[:limit], 1):
        title = r.get("title") or "Untitled"
        url = r.get("url") or ""
        content = (r.get("content") or "").replace("\n", " ").strip()
        score = r.get("score")
        lines.append(f"[{i}] {title}\nURL: {url}\nScore: {score}\nSnippet: {content}")
    return "\n\n".join(lines)
