"""Web search tool for agents."""

import json
from typing import Annotated, Any

import requests
from bs4 import BeautifulSoup

from ..utils.logger import get_logger

logger = get_logger(__name__)


def web_search(
    query: Annotated[str, "The search query to look up"],
    num_results: Annotated[int, "Number of results to return"] = 5,
) -> str:
    """
    Search the web for information.

    This is a simple web search tool that uses DuckDuckGo HTML search.
    For production, consider using Google Custom Search API or Bing Search API.

    Args:
        query: Search query
        num_results: Number of results to return (default: 5)

    Returns:
        JSON string with search results
    """
    logger.info(f"Web search: {query}")

    try:
        # Use DuckDuckGo HTML (no API key required)
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        response = requests.post(url, data=params, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML results
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        # Find search result divs
        result_divs = soup.find_all("div", class_="result")[:num_results]

        for div in result_divs:
            try:
                title_elem = div.find("a", class_="result__a")
                snippet_elem = div.find("a", class_="result__snippet")

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get("href", "")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    results.append({"title": title, "url": url, "snippet": snippet})
            except Exception as e:
                logger.warning(f"Error parsing result: {e}")
                continue

        if not results:
            return json.dumps(
                {"status": "no_results", "message": f"No results found for query: {query}"}
            )

        return json.dumps({"status": "success", "query": query, "results": results}, indent=2)

    except Exception as e:
        logger.error(f"Web search error: {e}")
        return json.dumps({"status": "error", "message": f"Search failed: {str(e)}"})


class WebSearchTool:
    """Web search tool wrapper for AutoGen."""

    @staticmethod
    def get_schema() -> dict[str, Any]:
        """Get tool schema for AutoGen."""
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for information using DuckDuckGo",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query"},
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return (1-10)",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
        }

    @staticmethod
    def execute(query: str, num_results: int = 5) -> str:
        """Execute web search."""
        return web_search(query, num_results)
