from .base import Strategy
class TemporaryInjunctionStrategy(Strategy):
    event_type="temporary_injunction"; label="Temporary Injunction"; fields=("urgency","prima_facie_case","balance_of_convenience")

