class CaseWorkspaceAgent:
    """Case-level orchestration equivalent to EquityNav's portfolio agent."""
    def snapshot(self, case: dict) -> dict:
        return {"case_id": case.get("id"), "case_name": case.get("case_name"), "matter_type": case.get("matter_type"), "risk_level": case.get("risk_level", "normal")}
    def attention_items(self, case: dict, documents: list[dict], events: list[dict]) -> list[dict]:
        items=[]
        if not documents: items.append({"priority":"high","title":"Case has no documents","next_step":"Upload the core pleadings, orders, notices, and evidence."})
        if case.get("next_hearing_date"): items.append({"priority":"high","title":"Upcoming hearing","due_date":case["next_hearing_date"]})
        items.extend({"priority": event.get("severity", "medium"), "title": event.get("title"), "due_date": event.get("event_date")} for event in events if event.get("status", "active") == "active")
        return items
