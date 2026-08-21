from .base import Strategy
class TheftBailStrategy(Strategy):
    event_type="theft_bail"; label="Theft / Bail"; fields=("offence_sections","custody_status","prior_record")

