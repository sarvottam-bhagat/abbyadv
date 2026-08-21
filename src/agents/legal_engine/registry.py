from src.agents.legal_engine.strategies.property_civil import PropertyCivilStrategy
from src.agents.legal_engine.strategies.family_matrimonial import FamilyMatrimonialStrategy
from src.agents.legal_engine.strategies.criminal import CriminalStrategy
from src.agents.legal_engine.strategies.consumer_rera import ConsumerReraStrategy
from src.agents.legal_engine.strategies.mact import MACTStrategy


STRATEGIES = {
    strategy.event_type: strategy()
    for strategy in (
        PropertyCivilStrategy,
        FamilyMatrimonialStrategy,
        CriminalStrategy,
        ConsumerReraStrategy,
        MACTStrategy,
    )
}
SCENARIOS = {
    event_type: (strategy.label, [field["name"] for field in strategy.field_specs])
    for event_type, strategy in STRATEGIES.items()
}


def scenario_types():
    return [strategy.form_schema() for strategy in STRATEGIES.values()]
