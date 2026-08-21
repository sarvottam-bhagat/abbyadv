"""Minimal async client for Indian Kanoon's documented search and document APIs."""

from __future__ import annotations

from dataclasses import dataclass
import html
import re
from typing import Any

import httpx

from src.core.config import get_settings


@dataclass(frozen=True)
class IndianKanoonSource:
    document_id: str
    title: str
    citation: str | None
    court: str | None
    date: str | None
    snippet: str
    url: str

    def as_dict(self) -> dict[str, str | None]:
        return {
            "source_type": "indian_kanoon",
            "document_id": self.document_id,
            "title": self.title,
            "citation": self.citation,
            "court": self.court,
            "date": self.date,
            "snippet": self.snippet,
            "url": self.url,
        }


class IndianKanoonClient:
    base_url = "https://api.indiankanoon.org"

    def __init__(self, api_token: str | None = None):
        self.api_token = api_token if api_token is not None else get_settings().indian_kanoon_api_token

    @property
    def configured(self) -> bool:
        return bool(self.api_token)

    async def search(self, query: str, limit: int = 5) -> list[IndianKanoonSource]:
        if not self.configured:
            raise RuntimeError("Indian Kanoon research is not configured. Add INDIAN_KANOON_API_TOKEN to the backend environment.")
        headers = {"Authorization": f"Token {self.api_token}", "Accept": "application/json"}
        params = {"formInput": query, "pagenum": 0, "maxcites": 5}
        async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
            # Indian Kanoon's official AJAX/client examples use POST even though the
            # query parameters are encoded in the URL. GET currently returns 405.
            response = await client.post(f"{self.base_url}/search/", params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        rows = data.get("docs") or data.get("results") or data.get("documents") or []
        sources: list[IndianKanoonSource] = []
        for row in rows[:limit]:
            if not isinstance(row, dict):
                continue
            doc_id = str(row.get("tid") or row.get("docid") or row.get("id") or "")
            if not doc_id:
                continue
            title = self._text(row.get("title") or row.get("headline")) or "Untitled authority"
            citation = self._text(row.get("citation") or row.get("cite"))
            court = self._text(row.get("court") or row.get("doctype") or row.get("court_name"))
            date = self._text(row.get("publishdate") or row.get("date") or row.get("decision_date"))
            snippet = self._text(row.get("headline") or row.get("snippet") or row.get("summary")) or title
            sources.append(IndianKanoonSource(doc_id, title, citation, court, date, snippet, f"https://indiankanoon.org/doc/{doc_id}/"))
        return sources

    @staticmethod
    def _text(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, list):
            return "; ".join(str(item) for item in value[:3])
        return html.unescape(re.sub(r"<[^>]+>", "", str(value))).strip()
