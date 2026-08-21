"""Structured, review-first scenario analysis strategies.

These strategies intentionally do not decide legal outcomes.  They turn the
advocate's inputs into a consistent case-review checklist that can later be
augmented with retrieved documents and cited research.
"""

from __future__ import annotations

from typing import Any


class Strategy:
    event_type = ""
    label = ""
    description = ""
    field_specs: tuple[dict[str, Any], ...] = ()
    key_issues: tuple[str, ...] = ()
    evidence_checklist: tuple[str, ...] = ()
    strength_factors: tuple[str, ...] = ()
    risk_factors: tuple[str, ...] = ()
    opponent_arguments: tuple[str, ...] = ()
    recommended_reliefs: tuple[str, ...] = ()
    next_steps: tuple[str, ...] = ()

    def form_schema(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "label": self.label,
            "description": self.description,
            "fields": list(self.field_specs),
        }

    def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        required = [field["name"] for field in self.field_specs if field.get("required", True)]
        missing_inputs = [field for field in required if not params.get(field)]
        provided_facts = {
            field["name"]: params[field["name"]]
            for field in self.field_specs
            if params.get(field["name"])
        }
        date_fields = [field["name"] for field in self.field_specs if field.get("type") == "date"]
        timeline = [
            {"event": field.replace("_", " ").title(), "date": str(params[field])}
            for field in date_fields
            if params.get(field)
        ]
        if not timeline:
            timeline.append({"event": "Chronology required", "date": "Add key incident, notice, filing, and hearing dates."})

        readiness = "ready_for_advocate_review" if not missing_inputs else "needs_more_information"
        return {
            "summary": f"{self.label} scenario prepared for advocate review.",
            "case_intake": {
                "practice_area": self.label,
                "facts_provided": provided_facts,
                "missing_intake_fields": missing_inputs,
            },
            "key_issues": list(self.key_issues),
            "missing_evidence": list(self.evidence_checklist),
            "timeline_builder": timeline,
            "strength_analysis": {
                "potential_strengths": list(self.strength_factors),
                "risks_or_uncertainties": list(self.risk_factors),
                "readiness": readiness,
            },
            "opponent_arguments": list(self.opponent_arguments),
            "recommended_reliefs": list(self.recommended_reliefs),
            "next_steps": list(self.next_steps),
            "filing_readiness": {
                "status": readiness,
                "before_filing": [
                    "Verify limitation and forum/jurisdiction.",
                    "Confirm every material fact against primary documents.",
                    "Have an advocate review the final pleadings and reliefs.",
                ],
            },
            "fact_evidence_matrix": [
                {"fact": "Add each material fact once documents are reviewed.", "source": "Intake states", "status": "missing"}
            ],
            "issue_analysis": [
                {
                    "issue": issue,
                    "facts": "Add the facts bearing on this issue.",
                    "applicable_law": "Add the applicable statute/provision once researched.",
                    "application": "Apply the law to this client's facts.",
                    "conclusion": "State the client's position on this issue.",
                }
                for issue in self.key_issues
            ],
            "opponent_rebuttal": [
                {"opponent_argument": argument, "our_rebuttal": "Add the fact-based rebuttal.", "supporting_facts": "Add supporting facts/documents."}
                for argument in self.opponent_arguments
            ],
            "filing_checklist": [
                {"item": "Verify limitation and forum/jurisdiction.", "status": "pending", "note": ""},
                {"item": "Confirm every material fact against primary documents.", "status": "pending", "note": ""},
                {"item": "Have an advocate review the final pleadings and reliefs.", "status": "pending", "note": ""},
            ],
            "missing_inputs": missing_inputs,
            "citations": [],
            "confidence": 0.55 if not missing_inputs else 0.35,
            "disclaimer": "Structured case-analysis aid only; it is not a legal opinion or a prediction of outcome.",
        }
