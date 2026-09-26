"""
Browser tools.
MVP implementation uses `webbrowser` to open real browser windows/tabs (for
open_browser/open_url/search_web) and `requests`+BeautifulSoup to fetch and
read page text non-interactively (read_page). Full in-page automation
(click/type inside a live browser) needs Selenium or Playwright; swap
read_page/click/type for a Playwright-backed implementation when you need
JS-rendered pages or real in-page interaction.
"""
import webbrowser
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import os


def open_browser(url: str = "https://www.google.com") -> dict:
    webbrowser.open(url)
    return {"success": True, "url": url}


def search_web(query: str, open_in_browser: bool = True) -> dict:
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    if open_in_browser:
        webbrowser.open(url)
    return {"success": True, "query": query, "url": url}


def open_url(url: str) -> dict:
    webbrowser.open(url)
    return {"success": True, "url": url}


def read_page(url: str, max_chars: int = 6000) -> dict:
    """Fetch a URL and extract visible text (non-JS-rendered pages only)."""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return {"success": True, "url": url, "text": text[:max_chars]}
    except Exception as e:
        return {"success": False, "error": str(e)}


def download(url: str, save_path: str) -> dict:
    try:
        resp = requests.get(url, timeout=20, stream=True)
        resp.raise_for_status()
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        return {"success": True, "path": os.path.abspath(save_path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Placeholders that require Selenium/Playwright for real in-page interaction.
def click(selector: str) -> dict:
    return {"success": False, "error": "click() needs a Playwright/Selenium-backed session. Not implemented in the requests-based MVP."}


def type_into(selector: str, text: str) -> dict:
    return {"success": False, "error": "type_into() needs a Playwright/Selenium-backed session. Not implemented in the requests-based MVP."}


TOOL_SCHEMAS = [
    {"name": "open_browser", "description": "Open the default browser at a URL.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}}},
    {"name": "search_web", "description": "Search the web for a query in the browser.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "open_in_browser": {"type": "boolean"}}, "required": ["query"]}},
    {"name": "open_url", "description": "Open a specific URL in the browser.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
    {"name": "read_page", "description": "Fetch a URL and extract its visible text content.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
    {"name": "download", "description": "Download a file from a URL to a local path.", "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "save_path": {"type": "string"}}, "required": ["url", "save_path"]}},
]
