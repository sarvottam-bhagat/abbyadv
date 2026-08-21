from .base import Strategy


class CriminalStrategy(Strategy):
    event_type = "criminal"
    label = "Criminal Matter"
    description = "Theft, assault, cheating/fraud, bail, FIR/quashing, and cybercrime analysis."
    field_specs = (
        {"name": "matter_type", "label": "Matter type", "type": "select", "options": ["Theft", "Assault", "Cheating / fraud", "Bail", "FIR quashing", "Cybercrime"], "required": True},
        {"name": "incident_summary", "label": "Incident summary", "type": "textarea", "required": True},
        {"name": "incident_date", "label": "Incident date", "type": "date", "required": True},
        {"name": "fir_status", "label": "FIR / complaint status", "type": "textarea", "required": True},
        {"name": "custody_status", "label": "Custody / bail status", "type": "text", "required": True},
        {"name": "defence_or_complainant_position", "label": "Client's position and immediate concern", "type": "textarea", "required": True},
    )
    key_issues = ("Alleged offence ingredients and available material", "Liberty, bail, and procedural stage", "Preservation of digital, documentary, and witness evidence")
    evidence_checklist = ("FIR/complaint, notices, remand/bail orders, and case diary material available to the client", "Chats, call records, CCTV, transaction trail, device records, or medical material as relevant", "Witness details and contemporaneous complaint/response")
    strength_factors = ("Objective contemporaneous records", "Clear inconsistency in allegation or absence of a key ingredient", "Cooperation, stable roots, and compliance material for bail")
    risk_factors = ("Custody, coercive action, or evidence-preservation urgency", "Digital evidence gaps or adverse contemporaneous material", "Multiple accused, prior cases, or witness-influence allegations")
    opponent_arguments = ("Material establishes the alleged offence and requires investigation", "Custodial interrogation or restrictive bail conditions are necessary", "Defence is an afterthought or civil dispute is being mischaracterised")
    recommended_reliefs = ("Appropriate bail/anticipatory-bail or protective remedy after advocate review", "Complaint/FIR representation, response, or investigation-stage application", "Preservation request for relevant electronic or documentary evidence")
    next_steps = ("Secure FIR/court papers and exact procedural status", "Preserve original devices and records without alteration", "Identify urgent liberty deadlines and prepare a verified chronology")
