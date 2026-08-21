from src.agents.legal_engine.registry import SCENARIOS
from src.agents.legal_engine.executor import LegalScenarioExecutor
from src.agents.legal_engine.scenario_agent import ScenarioAnalysisAgent
def run_scenario(event_type: str, params: dict) -> dict:
    return LegalScenarioExecutor().execute(event_type, params)


async def run_document_grounded_scenario(event_type: str, params: dict, case_context: dict, document_context: list[dict[str, str]]) -> dict:
    return await ScenarioAnalysisAgent().analyze(event_type, params, case_context, document_context)
