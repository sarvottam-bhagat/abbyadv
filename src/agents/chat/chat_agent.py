from dataclasses import dataclass
import json
from src.agents.retrieval.context_builder import RetrievalContextBuilder
from src.agents.retrieval.semantic_search import SemanticSearchAgent
from src.agents.retrieval.reranker import RetrievalReranker
from src.agents.chat.legal_scope import DECLINE_MESSAGE, LegalScopeGuard
from src.services.llm import LLMService
@dataclass
class ChatContext:
    client_ids: list[str]
    case_ids: list[str]
    document_ids: list[str]
    case_snapshot: list[dict] | None = None
    direct_attachment_text: str | None = None
class ChatAgent:
    def __init__(self, search_agent: SemanticSearchAgent | None = None):
        self.search_agent = search_agent or SemanticSearchAgent(); self.llm = LLMService(); self.scope_guard = LegalScopeGuard()
    async def answer(self, question: str, context: ChatContext, user_id: str | None = None) -> dict:
        decision = self.scope_guard.evaluate(question, has_case_context=bool(context.case_ids), has_document=bool(context.direct_attachment_text or context.document_ids))
        if not decision.allowed:
            return self._scope_result(context, decision.reason)
        prompt, results, retrieval_error = await self._prepare(question, context, user_id)
        answer = await self.llm.complete(self._system_prompt(), prompt)
        return self._result(answer, context, results, retrieval_error)

    async def stream_answer(self, question: str, context: ChatContext, user_id: str | None = None):
        decision = self.scope_guard.evaluate(question, has_case_context=bool(context.case_ids), has_document=bool(context.direct_attachment_text or context.document_ids))
        if not decision.allowed:
            result = self._scope_result(context, decision.reason)
            yield {"type": "token", "token": result["answer"]}
            yield {"type": "done", "result": result}
            return
        prompt, results, retrieval_error = await self._prepare(question, context, user_id)
        answer_parts: list[str] = []
        async for token in self.llm.stream(self._system_prompt(), prompt):
            answer_parts.append(token)
            yield {"type": "token", "token": token}
        yield {"type": "done", "result": self._result("".join(answer_parts) or "No answer was generated.", context, results, retrieval_error)}

    async def _prepare(self, question: str, context: ChatContext, user_id: str | None) -> tuple[str, list[dict], str | None]:
        results = []
        retrieval_error = None
        if user_id and (context.case_ids or context.document_ids):
            try:
                results = await self.search_agent.search(question, user_id, context.case_ids[0] if context.case_ids else None, context.document_ids[0] if context.document_ids else None)
                results = RetrievalReranker().rerank(results)
            except Exception as exc:
                retrieval_error = str(exc)
        evidence = RetrievalContextBuilder().build(results)
        if context.direct_attachment_text:
            direct_text = context.direct_attachment_text[:60_000]
            evidence = f"Direct chat attachment (read for this response only):\n{direct_text}\n\n{evidence}".strip()
        case_metadata = json.dumps(context.case_snapshot or [], default=str)
        return f"Question:\n{question}\n\nCase metadata:\n{case_metadata}\n\nCase-document context:\n{evidence}", results, retrieval_error

    def _result(self, answer: str, context: ChatContext, results: list[dict], retrieval_error: str | None) -> dict:
        trace = {"tool": "qdrant_case_retrieval", "status": "failed" if retrieval_error else "success", "result_count": len(results)}
        if retrieval_error: trace["error"] = retrieval_error
        return {"answer": answer, "citations": [{"document_id": r.get("payload", {}).get("document_id"), "score": r.get("score")} for r in results], "tool_trace": [trace], "confidence": 0.0 if not results else 0.5, "context": context.__dict__}

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are AbbyAdv, a legal-only advocate assistant. Answer only legal questions, legal-document review, "
            "case analysis, or legal drafting. Use only supplied context, distinguish facts from inference, flag "
            "uncertainty, and do not invent citations. If a prompt is not legal, politely decline and direct the user "
            "to legal work. Do not represent general model knowledge as verified legal research."
        )

    @staticmethod
    def _scope_result(context: ChatContext, reason: str | None) -> dict:
        return {
            "answer": DECLINE_MESSAGE,
            "citations": [],
            "tool_trace": [{"tool": "legal_scope_guard", "status": "blocked", "reason": reason}],
            "confidence": 1.0,
            "context": context.__dict__,
        }
