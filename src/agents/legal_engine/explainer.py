class LegalScenarioExplainer:
    def explain(self, result: dict) -> str: return result.get("summary", "")

