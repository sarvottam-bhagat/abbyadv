from .base import Strategy
class ChequeBounceStrategy(Strategy):
    event_type="cheque_bounce"; label="Cheque Bounce"; fields=("notice_date","dishonour_date","payment_received")

