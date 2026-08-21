from .base import Strategy


class MACTStrategy(Strategy):
    event_type = "mact"
    label = "Motor Accident Compensation (MACT)"
    description = "Road accident injury/death compensation and insurance dispute analysis."
    field_specs = (
        {"name": "accident_date", "label": "Accident date", "type": "date", "required": True},
        {"name": "injury_or_death", "label": "Injury or death details", "type": "textarea", "required": True},
        {"name": "vehicle_details", "label": "Vehicles and parties involved", "type": "textarea", "required": True},
        {"name": "fir_or_claim_status", "label": "FIR / claim petition status", "type": "textarea", "required": True},
        {"name": "insurer_details", "label": "Insurer / policy details", "type": "textarea", "required": True},
        {"name": "income_and_loss", "label": "Income, treatment, and loss details", "type": "textarea", "required": True},
    )
    key_issues = ("Accident involvement, negligence, and liability material", "Medical disability/dependency and income proof", "Insurer/policy status and compensation heads")
    evidence_checklist = ("FIR, site plan, charge sheet, MLC, and vehicle/policy records", "Medical bills, treatment records, disability certificate, and future-care material", "Income, dependency, age, and employment records")
    strength_factors = ("Contemporaneous police and medical record", "Clear insurance/policy and vehicle identification", "Well-documented treatment, disability, income, or dependency")
    risk_factors = ("Dispute on negligence or contributory negligence", "Missing policy, income, disability, or dependency evidence", "Inconsistent accident history across records")
    opponent_arguments = ("Claimant contributed to the accident", "Injury, disability, income, or expenses are overstated", "Policy breach or liability is disputed")
    recommended_reliefs = ("Compensation petition under the appropriate MACT forum", "Interim compensation/medical support where maintainable", "Compensation for treatment, income loss, disability/dependency, and costs as applicable")
    next_steps = ("Secure certified police, hospital, and insurance records", "Prepare treatment and income/dependency schedules", "Identify liable parties and verify tribunal jurisdiction")
