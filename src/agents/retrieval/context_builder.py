class RetrievalContextBuilder:
    def build(self, results: list[dict]) -> str:
        return "\n\n".join((result.get("payload") or {}).get("content", "") for result in results)

