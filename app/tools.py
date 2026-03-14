from __future__ import annotations

import os
from typing import Any

import httpx
from langchain_core.tools import tool


@tool
def serper_web_search(query: str) -> str:
    """Search the public web for latest banking, RBI, market, or regulation information using Serper."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "SERPER_API_KEY is not set. Web search is unavailable."

    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query}

    try:
        with httpx.Client(timeout=20) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
    except Exception as exc:
        return f"Web search failed: {exc}"

    organic = data.get("organic", [])[:5]
    if not organic:
        return "No useful public web results found."

    lines = []
    for item in organic:
        title = item.get("title", "No title")
        snippet = item.get("snippet", "")
        link = item.get("link", "")
        lines.append(f"Title: {title}\nSnippet: {snippet}\nLink: {link}")

    return "\n\n".join(lines)
