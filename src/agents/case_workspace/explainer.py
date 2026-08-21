class CaseExplainer:
    def explain(self, result: dict) -> str: return result.get("status", "unknown")

