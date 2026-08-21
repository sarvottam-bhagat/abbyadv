class ReportAgent:
    def build_case_summary(self, case: dict, scenario: dict | None = None) -> dict:
        result = scenario or {}
        return {"report_type": "case_summary", "title": case.get("case_name", "Case summary"), "case": case, "snapshot": {"matter_type": case.get("matter_type"), "stage": case.get("current_stage"), "risk_level": case.get("risk_level")}, "issues": result.get("issues", []), "evidence_gaps": result.get("evidence_gaps", []), "next_actions": result.get("next_actions", []), "citations": result.get("citations", [])}
