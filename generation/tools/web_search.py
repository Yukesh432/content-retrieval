from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, List, Dict

from langchain_community.tools.tavily_search import TavilySearchResults

class WebSearchClient:
    def __init__(self, max_results: int = 5):
        self.tool = TavilySearchResults(
            max_results=max_results,
            search_depth="advanced",
            include_answer=False,
            include_raw_content=False,
        )

    def search_compact(self, query: str, max_chars: int = 6000) -> str:
        try:
            results = self.tool.invoke({"query": query})
            print("Web search results:", results)
            print("+" * 40)
        except Exception as e:
            return f"Web Search Results:\n[WebSearchError] {type(e).__name__}: {e}"

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        lines = [f"Web Search Results (UTC date: {now})"]

        if isinstance(results, list):
            for i, r in enumerate(results, 1):
                title = (r.get("title") or "").strip()
                url = (r.get("url") or "").strip()
                snippet = (r.get("content") or r.get("snippet") or "").strip()
                snippet = snippet[:500]
                lines.append(f"{i}. {title}\n   {url}\n   {snippet}")
        else:
            lines.append(str(results)[:2000])

        text = "\n".join(lines)
        return text[:max_chars]