from .base import Strategy
class LegalNoticeReplyStrategy(Strategy):
    event_type="legal_notice_reply"; label="Legal Notice Reply"; fields=("notice_date","claims","response_position")

