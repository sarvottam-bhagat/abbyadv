from src.services.retrieval import retrieve
class SemanticSearchAgent:
    async def search(self, query: str, user_id: str, case_id: str | None = None, document_id: str | None = None, limit: int = 10):
        return await retrieve(query, user_id, case_id, document_id, limit)

