from .base import Strategy
class LandDisputeStrategy(Strategy):
    event_type="land_dispute"; label="Land Dispute"; fields=("property_type","claim_basis","possession_status","relief_sought")

