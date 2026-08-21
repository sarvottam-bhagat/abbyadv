from .base import Strategy


class ConsumerReraStrategy(Strategy):
    event_type = "consumer_rera"
    label = "Consumer / RERA Matter"
    description = "Defective products, deficient services, builder-buyer delay, refund, and RERA analysis."
    field_specs = (
        {"name": "dispute_type", "label": "Dispute type", "type": "select", "options": ["Defective product", "Deficient service", "Builder-buyer delay", "Delay in possession", "Refund claim"], "required": True},
        {"name": "provider_or_project", "label": "Seller, service provider, or project", "type": "text", "required": True},
        {"name": "amount_paid", "label": "Amount paid / claimed", "type": "text", "required": True},
        {"name": "deficiency_summary", "label": "Deficiency, delay, or misrepresentation", "type": "textarea", "required": True},
        {"name": "key_date", "label": "Purchase / promised-possession / key date", "type": "date", "required": True},
        {"name": "notice_or_complaint_status", "label": "Notice or complaint status", "type": "textarea", "required": True},
    )
    key_issues = ("Consumer/RERA forum and maintainability", "Deficiency, delay, representations, and contractual terms", "Refund, possession, compensation, interest, and costs")
    evidence_checklist = ("Booking/order form, agreement, invoices, and payment proof", "Advertisements, promises, emails, notices, and complaint acknowledgements", "Project status/approval material or service reports and photographs")
    strength_factors = ("Written promise with traceable payment", "Clear delay or documented deficiency", "Timely complaint and consistent consumer communications")
    risk_factors = ("Contractual exclusions or disputed milestones", "Forum/limitation uncertainty", "Incomplete evidence of loss, deficiency, or promised delivery date")
    opponent_arguments = ("Delay arose from force majeure, buyer default, or agreed variation", "No actionable deficiency or consumer relationship", "Claim/compensation is excessive or time-barred")
    recommended_reliefs = ("Refund with applicable interest where facts support it", "Possession/completion direction or rectification", "Compensation, costs, and appropriate interim protection")
    next_steps = ("Reconcile every payment against the agreement", "Prepare a promise-versus-performance chronology", "Check appropriate consumer commission/RERA forum and limitation")
