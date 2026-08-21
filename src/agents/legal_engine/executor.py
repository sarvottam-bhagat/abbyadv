from src.agents.legal_engine.registry import SCENARIOS, STRATEGIES
class LegalScenarioExecutor:
    def execute(self, event_type: str, params: dict) -> dict:
        strategy = STRATEGIES.get(event_type)
        if strategy: return strategy.execute(params)
        label = SCENARIOS.get(event_type, (event_type, []))[0]
        return {"summary": f"{label} assessment created for advocate review.", "issues": [], "evidence_gaps": [], "next_actions": [], "citations": [], "confidence": 0.0, "disclaimer": "Deterministic MVP output; not legal advice."}
