"""
Research engine: search multiple sources, read them, and ask the LLM to
compare/summarize with citations. Depends on browser.py for fetching and
agent.llm_client for summarization, so it is intentionally the most "composed"
tool - it calls other tools rather than doing raw I/O itself.
"""
import sys
import os
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.browser import read_page
from agent.llm_client import LLMClient


def _search_result_links(query: str, max_links: int = 5) -> list:
    """Scrape a handful of result links from DuckDuckGo's HTML endpoint (no API key needed)."""
    try:
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.select("a.result__a")[:max_links]:
            href = a.get("href")
            if href:
                links.append(href)
        return links
    except Exception:
        return []


def research(topic: str, max_sources: int = 4) -> dict:
    links = _search_result_links(topic, max_links=max_sources)
    if not links:
        return {"success": False, "error": "No sources found (search scraping may be blocked - swap in a proper search API)."}

    sources = []
    for url in links:
        page = read_page(url, max_chars=3000)
        if page.get("success"):
            sources.append({"url": url, "text": page["text"]})

    if not sources:
        return {"success": False, "error": "Found links but could not read any of them."}

    llm = LLMClient()
    context = "\n\n".join(f"SOURCE ({s['url']}):\n{s['text']}" for s in sources)
    prompt = (
        f"Research topic: {topic}\n\n"
        f"Using only the sources below, write a concise, well-organized summary. "
        f"Compare differing viewpoints if any exist, and cite each claim with its source URL "
        f"in parentheses.\n\n{context}"
    )
    summary = llm.simple_complete(prompt)
    return {"success": True, "topic": topic, "sources": [s["url"] for s in sources], "summary": summary}


TOOL_SCHEMAS = [
    {
        "name": "research",
        "description": "Research a topic across multiple web sources and produce a cited summary.",
        "input_schema": {"type": "object", "properties": {"topic": {"type": "string"}, "max_sources": {"type": "integer"}}, "required": ["topic"]},
    },
]
