"""Small, deterministic guard that keeps AbbyAdv focused on legal work."""

from __future__ import annotations

from dataclasses import dataclass
import re


OUT_OF_SCOPE_PATTERNS = (
    r"\bwhat is python\b", r"\bpython (programming|code|language)\b",
    r"\bwrite (?:a )?(?:python|javascript|java|react|sql)\b",
    r"\bdebug (?:my )?(?:code|app|program)\b", r"\bweather\b",
    r"\brecipe\b", r"\bmovie\b", r"\bcricket score\b",
    r"\bbitcoin price\b", r"\bstock price\b",
)

LEGAL_SIGNALS = (
    "legal", "law", "court", "judge", "judgment", "judgement", "case law", "precedent",
    "act", "section", "article", "statute", "rule", "regulation", "tribunal", "fir", "cnr",
    "notice", "contract", "agreement", "clause", "litigation", "petition", "appeal", "bail",
    "injunction", "property", "tenant", "landlord", "divorce", "custody", "crime", "criminal",
    "civil", "sue", "claim", "rights", "damages", "liability", "compensation", "arrest", "police",
    "employer", "employee", "company", "employment", "labour", "labor", "tax", "gst", "ip", "copyright",
    "trademark", "consumer", "succession", "will", "inheritance", "compliance", "dispute",
    "remedy", "limitation", "hearing", "advocate", "lawyer", "plaintiff", "defendant", "respondent",
)

DECLINE_MESSAGE = (
    "AbbyAdv is focused on legal research, case analysis, document review, and drafting. "
    "Please ask a legal question or attach a document whose legal implications you want reviewed."
)


@dataclass(frozen=True)
class ScopeDecision:
    allowed: bool
    reason: str | None = None


class LegalScopeGuard:
    """Reject clear non-legal prompts while allowing matter/document-context work."""

    def evaluate(self, question: str, *, has_case_context: bool = False, has_document: bool = False) -> ScopeDecision:
        normalized = re.sub(r"\s+", " ", question.lower()).strip()
        if not normalized:
            return ScopeDecision(False, "empty")
        if any(re.search(pattern, normalized) for pattern in OUT_OF_SCOPE_PATTERNS):
            return ScopeDecision(False, "clear_non_legal")
        # A selected case or an attached document is evidence work. Let the legal assistant
        # decide its legal relevance rather than rejecting an evidence-specific question.
        if has_case_context or has_document:
            return ScopeDecision(True)
        if any(signal in normalized for signal in LEGAL_SIGNALS):
            return ScopeDecision(True)
        return ScopeDecision(False, "not_legal")
