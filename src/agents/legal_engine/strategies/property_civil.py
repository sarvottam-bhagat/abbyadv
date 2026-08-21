from .base import Strategy


class PropertyCivilStrategy(Strategy):
    event_type = "property_civil"
    label = "Property / Civil Dispute"
    description = "Partition, ownership, encroachment, injunction, or agreement-to-sell analysis."
    field_specs = (
        {"name": "dispute_type", "label": "Dispute type", "type": "select", "options": ["Ownership", "Partition", "Encroachment", "Specific performance", "Injunction"], "required": True},
        {"name": "property_description", "label": "Property and location", "type": "text", "required": True},
        {"name": "claim_basis", "label": "Client's claim basis", "type": "textarea", "required": True},
        {"name": "possession_status", "label": "Current possession status", "type": "text", "required": True},
        {"name": "opposite_party_position", "label": "Opponent's position", "type": "textarea", "required": True},
        {"name": "key_event_date", "label": "Key breach / incident date", "type": "date", "required": True},
        {"name": "urgency", "label": "Immediate risk or urgency", "type": "textarea", "required": False},
    )
    key_issues = ("Title or contractual right", "Possession and threatened dispossession/transfer", "Appropriate civil forum and limitation")
    evidence_checklist = ("Title chain, revenue records, and encumbrance search", "Agreement, payment proof, notices, and correspondence", "Site photographs, survey/measurement records, and possession evidence")
    strength_factors = ("Clear documentary title or written agreement", "Traceable payment and timely written demands", "Documented threat of alienation, encroachment, or dispossession")
    risk_factors = ("Unclear title chain or competing claims", "Delay, limitation, readiness/willingness, or possession disputes", "Missing property identification, approvals, or enforceability issues")
    opponent_arguments = ("Client lacks title or was not ready and willing to perform", "Payment/possession terms were not fulfilled", "Claim is delayed, barred, or property cannot be specifically enforced")
    recommended_reliefs = ("Appropriate declaration or specific performance relief", "Temporary/interim injunction pending suit where facts justify it", "Possession, partition, mesne profits, damages, or costs as applicable")
    next_steps = ("Prepare a document-backed chronology", "Run title/encumbrance and forum checks", "Preserve proof of urgency before seeking interim protection")
