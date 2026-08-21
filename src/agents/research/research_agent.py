"""Public-authority research agent, intentionally separate from private case chat."""

from __future__ import annotations

import json
import logging
import re

from src.agents.chat.chat_agent import ChatContext
from src.agents.chat.legal_scope import DECLINE_MESSAGE, LegalScopeGuard
from src.agents.retrieval.context_builder import RetrievalContextBuilder
from src.agents.retrieval.reranker import RetrievalReranker
from src.agents.retrieval.semantic_search import SemanticSearchAgent
from src.services.indian_kanoon import IndianKanoonClient
from src.services.ecourts import ECourtsClient
from src.services.llm import LLMService

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Combine private matter context with cited Indian Kanoon authorities.

    Only the user's legal query is sent to Indian Kanoon. Private case metadata and
    document contents remain inside AbbyAdv and are supplied only to the LLM.
    """

    def __init__(self, indian_kanoon: IndianKanoonClient | None = None, search_agent: SemanticSearchAgent | None = None, ecourts: ECourtsClient | None = None):
        self.indian_kanoon = indian_kanoon or IndianKanoonClient()
        self.ecourts = ecourts or ECourtsClient()
        self.search = search_agent or SemanticSearchAgent()
        self.llm = LLMService()
        self.scope_guard = LegalScopeGuard()

    async def run(self, query: str, user_id: str, case_id: str | None = None) -> dict:
        context = ChatContext([], [case_id] if case_id else [], [])
        return await self.answer(query, context, user_id)

    async def answer(self, question: str, context: ChatContext, user_id: str | None = None) -> dict:
        decision = self.scope_guard.evaluate(question, has_case_context=bool(context.case_ids), has_document=bool(context.direct_attachment_text or context.document_ids))
        if not decision.allowed:
            return self._scope_result(context, decision.reason)
        if not getattr(self.ecourts, "configured", False) and not getattr(self.indian_kanoon, "configured", False):
            return self._provider_unavailable_result(context)
        prompt, private_results, authorities, traces = await self._prepare(question, context, user_id)
        answer = await self.llm.complete(self._system_prompt(), prompt)
        return self._result(answer, context, private_results, authorities, traces)

    async def stream_answer(self, question: str, context: ChatContext, user_id: str | None = None):
        decision = self.scope_guard.evaluate(question, has_case_context=bool(context.case_ids), has_document=bool(context.direct_attachment_text or context.document_ids))
        if not decision.allowed:
            result = self._scope_result(context, decision.reason)
            yield {"type": "token", "token": result["answer"]}
            yield {"type": "done", "result": result}
            return
        if not getattr(self.ecourts, "configured", False) and not getattr(self.indian_kanoon, "configured", False):
            result = self._provider_unavailable_result(context)
            yield {"type": "token", "token": result["answer"]}
            yield {"type": "done", "result": result}
            return
        prompt, private_results, authorities, traces = await self._prepare(question, context, user_id)
        answer_parts: list[str] = []
        async for token in self.llm.stream(self._system_prompt(), prompt):
            answer_parts.append(token)
            yield {"type": "token", "token": token}
        yield {"type": "done", "result": self._result("".join(answer_parts) or "No research answer was generated.", context, private_results, authorities, traces)}

    async def _prepare(self, question: str, context: ChatContext, user_id: str | None) -> tuple[str, list[dict], list[dict], list[dict]]:
        private_results: list[dict] = []
        traces: list[dict] = []
        if user_id and (context.case_ids or context.document_ids):
            try:
                private_results = await self.search.search(question, user_id, context.case_ids[0] if context.case_ids else None, context.document_ids[0] if context.document_ids else None)
                private_results = RetrievalReranker().rerank(private_results)
                traces.append({"tool": "qdrant_case_retrieval", "status": "success", "result_count": len(private_results)})
            except Exception as exc:
                traces.append({"tool": "qdrant_case_retrieval", "status": "failed", "error": str(exc), "result_count": 0})

        authorities: list[dict] = []
        external_query = self._ecourts_query(question, context)
        if getattr(self.ecourts, "configured", False):
            try:
                # This is a neutral legal-issue query. Names, amounts, and private case
                # documents remain in AbbyAdv; eCourts receives no private matter data.
                authorities = [source.as_dict(external_query) for source in await self.ecourts.research(external_query, limit=2)]
                traces.append({"tool": "ecourts_judgment_evidence", "status": "success", "result_count": len(authorities), "query": external_query})
            except Exception as exc:
                logger.warning("eCourts research failed; trying Indian Kanoon fallback: %s", exc)
                traces.append({"tool": "ecourts_judgment_evidence", "status": "failed", "error": str(exc), "result_count": 0})

        # Indian Kanoon complements eCourts rather than replacing it: it is used
        # for broad authority discovery while eCourts supplies current order text.
        # This also preserves a cited answer if eCourts has no matching judgment.
        if getattr(self.indian_kanoon, "configured", False):
            try:
                # Only the user question is sent to this public provider; private
                # case metadata and documents remain inside AbbyAdv.
                # Search a wider candidate set because provider ranking may place
                # tax/privacy results before a directly matching civil judgment.
                indian_kanoon_sources = [source.as_dict() for source in await self.indian_kanoon.search(question, limit=12)]
                indian_kanoon_sources = [
                    source for source in indian_kanoon_sources
                    if self._authority_matches_issue(source, question)
                ][:3]
                authorities.extend(indian_kanoon_sources)
                traces.append({"tool": "indian_kanoon_legal_research", "status": "success", "result_count": len(indian_kanoon_sources)})
            except Exception as exc:
                logger.warning("Indian Kanoon research failed: %s", exc)
                traces.append({"tool": "indian_kanoon_legal_research", "status": "failed", "error": str(exc), "result_count": 0})

        private_evidence = RetrievalContextBuilder().build(private_results)
        if context.direct_attachment_text:
            private_evidence = f"Direct chat attachment (private; read for this response only):\n{context.direct_attachment_text[:60_000]}\n\n{private_evidence}".strip()
        authority_evidence = "\n\n".join(
            f"[{index + 1}] {item['title']}\nCourt/type: {item.get('court') or 'Not stated'}\n"
            f"Citation: {item.get('citation') or 'Not stated'}\nDate: {item.get('date') or 'Not stated'}\n"
            f"Excerpt: {item.get('snippet') or 'Not stated'}\nURL: {item['url']}"
            for index, item in enumerate(authorities)
        ) or "No external authority was retrieved. State that legal research sources are unavailable; do not invent them."
        prompt = (
            f"Legal research question:\n{question}\n\n"
            f"Private case metadata (never cite as public authority):\n{json.dumps(context.case_snapshot or [], default=str)}\n\n"
            f"Private case/document evidence (never cite as public authority):\n{private_evidence or 'None'}\n\n"
            f"External court authorities with complete order text (cite only these using [1], [2], etc.):\n{authority_evidence}"
        )
        return prompt, private_results, authorities, traces

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are AbbyAdv Legal Research. Answer only legal questions. Give a concise practical analysis, clearly "
            "separate private case facts from public legal research, and flag missing facts or uncertainty. Cite external "
            "authorities only with their supplied bracket number such as [1]. Put a citation immediately after every legal "
            "proposition grounded in an authority. Never invent an authority, citation, case "
            "holding, statutory provision, or URL. If no authority is supplied, say external legal research is unavailable. "
            "Distinguish a temporary/interim injunction sought pending the suit from a permanent injunction granted by the final decree; "
            "do not label one as the other. "
            "End with 'Sources consulted' listing only the supplied source numbers used. This is legal information, not a "
            "substitute for the advocate's professional judgment."
        )

    @staticmethod
    def _authority_matches_issue(source: dict, query: str) -> bool:
        """Reject broad-search results that do not match the advocate's issue."""
        stop_words = {
            "about", "against", "agreement", "applicable", "based", "court", "courts", "find", "from", "have", "indian",
            "legal", "party", "question", "relevant", "should", "that", "their", "third", "under", "what", "with",
        }
        query_terms = {
            term for term in re.findall(r"[a-z0-9]+", query.lower())
            if len(term) >= 4 and term not in stop_words
        }
        # Broad questions (for example a limitation-period query) do not have
        # enough discriminating terms for safe lexical filtering.
        if len(query_terms) < 4:
            return True
        haystack = " ".join(str(source.get(field) or "") for field in ("title", "snippet", "citation")).lower()
        matched = sum(1 for term in query_terms if term in haystack)
        return matched >= 2

    @staticmethod
    def _result(answer: str, context: ChatContext, private_results: list[dict], authorities: list[dict], traces: list[dict]) -> dict:
        private_citations = [{"source_type": "case_document", "document_id": item.get("payload", {}).get("document_id"), "score": item.get("score")} for item in private_results]
        return {
            "answer": answer,
            "citations": [*authorities, *private_citations],
            "sources": authorities,
            "tool_trace": traces,
            "confidence": 0.7 if authorities else (0.45 if private_results else 0.0),
            "context": context.__dict__,
        }

    @staticmethod
    def _scope_result(context: ChatContext, reason: str | None) -> dict:
        return {"answer": DECLINE_MESSAGE, "citations": [], "sources": [], "tool_trace": [{"tool": "legal_scope_guard", "status": "blocked", "reason": reason}], "confidence": 1.0, "context": context.__dict__}

    @staticmethod
    def _provider_unavailable_result(context: ChatContext) -> dict:
        return {
            "answer": "Legal Research is not configured yet. Add `ECOURTS_API_KEY` (or `INDIAN_KANOON_API_TOKEN` for the fallback provider) to the AbbyAdv backend environment, then retry to receive cited authorities.",
            "citations": [],
            "sources": [],
            "tool_trace": [{"tool": "indian_kanoon_legal_research", "status": "unavailable", "reason": "missing_api_token"}],
            "confidence": 0.0,
            "context": context.__dict__,
        }

    @staticmethod
    def _ecourts_query(question: str, context: ChatContext) -> str:
        """Create a non-identifying research query from the legal issue, not case PII."""
        # Case snapshots include SQLAlchemy date values (for hearings/limitation).
        # They are only used locally to classify the legal issue, so stringify them
        # before building the neutral external search query.
        combined = " ".join([question, json.dumps(context.case_snapshot or [], default=str)]).lower()
        if any(word in combined for word in ("sale deed", "agreement to sell", "developer", "possession", "property")):
            return "agreement to sell specific performance sale deed possession interim injunction third party transfer"
        if any(word in combined for word in ("employment", "employee", "termination", "salary", "dismissal")):
            return "employment termination wrongful dismissal compensation injunction"
        if any(word in combined for word in ("cheque", "138", "negotiable instrument")):
            return "negotiable instruments act section 138 cheque dishonour"
        # Generic research is user-initiated; remove likely names/numbers before the
        # query leaves AbbyAdv while retaining legal terms supplied by the advocate.
        cleaned = re.sub(r"\b[A-Z][a-z]{2,}\b", "", question)
        cleaned = re.sub(r"₹\s?[\d,]+|\b\d[\d,]*\b", "", cleaned)
        return re.sub(r"\s+", " ", cleaned).strip()[:300] or "Indian legal precedent"
