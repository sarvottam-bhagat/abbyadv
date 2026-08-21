from .base import Strategy


class FamilyMatrimonialStrategy(Strategy):
    event_type = "family_matrimonial"
    label = "Family & Matrimonial Matter"
    description = "Divorce, custody, maintenance, domestic violence, and guardianship analysis."
    field_specs = (
        {"name": "matter_type", "label": "Matter type", "type": "select", "options": ["Mutual divorce", "Contested divorce", "Child custody", "Maintenance", "Domestic violence", "Guardianship"], "required": True},
        {"name": "relationship_details", "label": "Relationship and marriage details", "type": "textarea", "required": True},
        {"name": "separation_date", "label": "Separation / key incident date", "type": "date", "required": True},
        {"name": "children_details", "label": "Children and current care arrangement", "type": "textarea", "required": False},
        {"name": "financial_position", "label": "Known income, expenses, and support position", "type": "textarea", "required": True},
        {"name": "immediate_relief", "label": "Immediate relief sought", "type": "textarea", "required": True},
    )
    key_issues = ("Grounds and procedural route", "Child welfare and interim arrangements where relevant", "Maintenance, protection, residence, and financial disclosure")
    evidence_checklist = ("Marriage, identity, residence, and children records", "Messages, complaints, medical records, or incident evidence where relevant", "Income records, bank statements, expenses, and existing orders")
    strength_factors = ("Contemporaneous records and consistent chronology", "Clear child-welfare or financial evidence", "Documented attempts at resolution where relevant")
    risk_factors = ("Conflicting allegations with little corroboration", "Incomplete financial disclosure", "Urgent safety or child-contact issues requiring immediate safeguards")
    opponent_arguments = ("Allegations are exaggerated or unsupported", "Applicant has sufficient independent means", "Requested custody/access arrangement is not in the child's welfare")
    recommended_reliefs = ("Appropriate matrimonial/family-court petition", "Interim maintenance, custody/access, protection, or residence relief where applicable", "Mediation/settlement terms if safely appropriate")
    next_steps = ("Create a date-wise relationship and incident chronology", "Collect financial and child-welfare material", "Assess immediate safety and interim-relief requirements")
