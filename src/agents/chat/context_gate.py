class ContextGate:
    def validate(self, client_ids: list[str], case_ids: list[str], document_ids: list[str]) -> dict:
        return {"client_ids": client_ids, "case_ids": case_ids, "document_ids": document_ids}

