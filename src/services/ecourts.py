"""Evidence-first eCourtsIndia client for legal research.

Only uses Case Search and Case Detail. Case Detail already includes complete
order markdown when available, so we deliberately avoid costly PDF/AI endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from src.core.config import get_settings


@dataclass(frozen=True)
class ECourtsAuthority:
    cnr: str
    title: str
    court: str | None
    date: str | None
    case_category: str | None
    text: str
    url: str

    def as_dict(self, query: str = "") -> dict[str, str | None]:
        return {
            "source_type": "ecourtsindia",
            "document_id": self.cnr,
            "title": self.title,
            "citation": self.cnr,
            "court": self.court,
            "date": self.date,
            "snippet": self._relevant_excerpt(query),
            "url": self.url,
        }

    def _relevant_excerpt(self, query: str) -> str:
        """Select passages related to the legal issue instead of sending order headers."""
        normalized = self.text.replace("\r", "")
        lower = normalized.lower()
        phrases = ["specific performance", "agreement to sell", "sale deed", "injunction", "possession", "third party"]
        phrases.extend(term for term in query.lower().split() if len(term) > 5)
        positions: list[int] = []
        for phrase in phrases:
            position = lower.find(phrase)
            if position >= 0 and all(abs(position - existing) > 700 for existing in positions):
                positions.append(position)
            if len(positions) == 4:
                break
        if not positions:
            return normalized[:6000]
        excerpts = []
        for position in positions:
            start = max(0, position - 500)
            end = min(len(normalized), position + 1300)
            excerpts.append(normalized[start:end])
        return "\n\n--- Relevant order passage ---\n\n".join(excerpts)[:7000]


class ECourtsClient:
    base_url = "https://webapi.ecourtsindia.com/api/partner"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key if api_key is not None else get_settings().ecourts_api_key

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise RuntimeError("eCourtsIndia is not configured. Add ECOURTS_API_KEY to the backend environment.")
        return {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}

    async def research(self, query: str, limit: int = 3) -> list[ECourtsAuthority]:
        """Search and read at most two source orders to control credit usage."""
        async with httpx.AsyncClient(timeout=35.0, follow_redirects=True) as client:
            response = await client.get(f"{self.base_url}/search", params={"query": query, "pageSize": max(5, limit)}, headers=self._headers())
            response.raise_for_status()
            payload = response.json().get("data", {})
            candidates = payload.get("results", [])
            authorities: list[ECourtsAuthority] = []
            for candidate in candidates:
                if len(authorities) >= min(limit, 2):
                    break
                cnr = str(candidate.get("cnr") or "")
                if not cnr or not candidate.get("hasJudgments"):
                    continue
                detail_response = await client.get(f"{self.base_url}/case/{cnr}", headers=self._headers())
                detail_response.raise_for_status()
                authority = self._authority_from_detail(candidate, detail_response.json().get("data", {}))
                if authority is not None:
                    authorities.append(authority)
            return authorities

    @staticmethod
    def _authority_from_detail(search_row: dict[str, Any], detail: dict[str, Any]) -> ECourtsAuthority | None:
        case_data = detail.get("courtCaseData") or detail.get("caseData") or detail
        files_container = detail.get("files") or case_data.get("files") or {}
        files = files_container.get("files") if isinstance(files_container, dict) else files_container
        markdown = ""
        if isinstance(files, list):
            for item in files:
                if isinstance(item, dict) and item.get("markdownContent"):
                    markdown = str(item["markdownContent"])
                    break
        if not markdown:
            return None
        petitioners = search_row.get("petitioners") or case_data.get("petitioners") or []
        respondents = search_row.get("respondents") or case_data.get("respondents") or []
        title = f"{', '.join(petitioners[:1]) or 'Petitioner'} v. {', '.join(respondents[:1]) or 'Respondent'}"
        cnr = str(search_row.get("cnr") or case_data.get("cnr") or "")
        return ECourtsAuthority(
            cnr=cnr,
            title=title,
            court=str(search_row.get("courtName") or case_data.get("courtName") or "") or None,
            date=str(search_row.get("decisionDate") or case_data.get("decisionDate") or "") or None,
            case_category=str(search_row.get("caseCategory") or case_data.get("caseCategory") or "") or None,
            text=markdown,
            url=f"https://ecourtsindia.com/cnr/{cnr}",
        )
