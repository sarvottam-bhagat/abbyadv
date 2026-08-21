class RetrievalReranker:
    def rerank(self, results: list[dict]) -> list[dict]: return sorted(results, key=lambda item: item.get("score", 0), reverse=True)

