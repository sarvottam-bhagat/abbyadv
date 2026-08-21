# API Spec

Base prefix:

```text
/api
```

All endpoints require authenticated user unless noted.

## Health

### GET `/health`

Returns service status.

Response:

```json
{
  "status": "ok"
}
```

## Users

### GET `/api/me`

Returns current advocate profile.

### PATCH `/api/me`

Updates advocate profile.

Payload:

```json
{
  "full_name": "Sarvottam Bhagat",
  "firm_name": "Bhagat Law Office",
  "phone": "+91...",
  "default_state": "DL"
}
```

## Clients

### POST `/api/clients`

Create client.

Payload:

```json
{
  "full_name": "Rajesh Sharma",
  "email": "rajesh@example.com",
  "phone": "+91...",
  "client_type": "individual",
  "city": "Delhi",
  "state": "DL",
  "country": "IN",
  "notes": "Property dispute client"
}
```

### GET `/api/clients`

List clients.

Query:

- `q`
- `status`
- `risk_level`
- `limit`
- `offset`

### GET `/api/clients/{client_id}`

Get client detail.

### PATCH `/api/clients/{client_id}`

Update client.

### DELETE `/api/clients/{client_id}`

Archive or delete client. Prefer archive in product flow.

## Cases

### POST `/api/clients/{client_id}/cases`

Create case under client.

Payload:

```json
{
  "case_name": "Rajesh Land Dispute",
  "matter_type": "property",
  "country": "IN",
  "state": "DL",
  "court_name": "Civil Court Delhi",
  "court_type": "civil_court",
  "case_number": "CS/123/2026",
  "client_role": "plaintiff",
  "opposite_party_name": "Mahesh Sharma",
  "current_stage": "injunction_hearing",
  "next_hearing_date": "2026-07-18",
  "relief_sought": "Temporary injunction",
  "facts_summary": "Opposite party started construction on disputed plot."
}
```

### GET `/api/clients/{client_id}/cases`

List cases for client.

### GET `/api/cases/{case_id}`

Get case detail.

### PATCH `/api/cases/{case_id}`

Update case.

### DELETE `/api/cases/{case_id}`

Archive/delete case.

## Documents

### POST `/api/documents/upload-url`

Create upload URL and document placeholder.

Payload:

```json
{
  "client_id": "...",
  "case_id": "...",
  "file_name": "sale_deed.pdf",
  "mime_type": "application/pdf",
  "document_type": "sale_deed"
}
```

Response:

```json
{
  "document_id": "...",
  "upload_url": "...",
  "storage_key": "case-documents/user/case/file.pdf"
}
```

### POST `/api/documents/{document_id}/process`

Starts OCR/text extraction/embedding.

Payload:

```json
{
  "use_ocr": true,
  "ocr_provider": "abbyy"
}
```

### GET `/api/documents/{document_id}`

Get document status/detail.

### GET `/api/cases/{case_id}/documents`

List case documents.

### DELETE `/api/documents/{document_id}`

Delete document and chunks.

## Chat

### POST `/api/chat`

Create message and process asynchronously.

Payload:

```json
{
  "question": "What urgent relief should we seek?",
  "session_id": null,
  "client_ids": ["..."],
  "case_ids": ["..."],
  "document_ids": ["..."],
  "mode": "chat"
}
```

Response:

```json
{
  "session_id": "...",
  "message_id": "...",
  "status": "pending",
  "message": "Message queued"
}
```

### GET `/api/chat/sessions`

List chat sessions.

### GET `/api/chat/sessions/{session_id}`

Get session with messages.

### GET `/api/chat/messages/{message_id}/status`

Poll message status.

### GET `/api/chat/stream/{message_id}`

SSE stream for answer.

### DELETE `/api/chat/sessions/{session_id}`

Delete session.

## Scenarios

### GET `/api/scenarios/types`

Returns supported scenario types and form schemas.

Response:

```json
{
  "types": [
    {
      "event_type": "land_dispute",
      "label": "Land Dispute",
      "fields": []
    }
  ]
}
```

### POST `/api/scenarios`

Create and run scenario.

Payload:

```json
{
  "client_id": "...",
  "case_id": "...",
  "name": "Rajesh injunction strategy",
  "event_type": "land_dispute",
  "country": "IN",
  "state": "DL",
  "input_parameters": {
    "property_type": "residential_plot",
    "claim_basis": "registered_sale_deed",
    "possession_status": "client_in_possession",
    "relief_sought": "temporary_injunction"
  },
  "document_ids": ["..."]
}
```

Response:

```json
{
  "scenario_id": "...",
  "status": "pending"
}
```

### GET `/api/scenarios/{scenario_id}`

Get scenario detail/result.

### GET `/api/cases/{case_id}/scenarios`

List scenarios for case.

### GET `/api/scenarios/{scenario_id}/status`

Poll scenario status.

### DELETE `/api/scenarios/{scenario_id}`

Delete scenario.

## Drafts

### POST `/api/drafts`

Create draft manually or from context.

Payload:

```json
{
  "client_id": "...",
  "case_id": "...",
  "scenario_id": "...",
  "draft_type": "injunction_application",
  "title": "Order 39 Application",
  "source_prompt": "Draft an urgent temporary injunction application."
}
```

### GET `/api/drafts`

List drafts.

Query:

- `client_id`
- `case_id`
- `draft_type`
- `status`

### GET `/api/drafts/{draft_id}`

Get draft.

### PATCH `/api/drafts/{draft_id}`

Update draft content/status.

### POST `/api/drafts/{draft_id}/improve`

AI improvement operation.

Payload:

```json
{
  "instruction": "Make this more formal and add citation placeholders."
}
```

### POST `/api/drafts/{draft_id}/export`

Create DOCX/PDF export job.

## Research

### POST `/api/research`

Run legal research.

Payload:

```json
{
  "query": "Relevant precedents for temporary injunction in land dispute",
  "client_id": "...",
  "case_id": "...",
  "country": "IN",
  "state": "DL",
  "sources": ["legal_rag", "indian_kanoon", "web"]
}
```

Response:

```json
{
  "memo_id": "...",
  "status": "processing"
}
```

### GET `/api/research/{memo_id}`

Get research memo.

### GET `/api/cases/{case_id}/research`

List research memos for case.

### POST `/api/research/{memo_id}/send-to-draft`

Create draft from research memo.

### POST `/api/research/{memo_id}/send-to-chat`

Attach research memo to chat context.

## Events / Action Items

### GET `/api/events`

List legal events.

Query:

- `from_date`
- `to_date`
- `client_id`
- `case_id`
- `severity`
- `status`

### POST `/api/events`

Create manual event/hearing/deadline.

### PATCH `/api/events/{event_id}`

Update event.

### GET `/api/action-items`

List action items.

### PATCH `/api/action-items/{action_item_id}`

Update action item status.

## Dashboard

### GET `/api/dashboard/summary`

Returns:

- total clients
- active cases
- hearings this week
- critical action items
- pending drafts
- pending document processing
- matter type breakdown

### GET `/api/dashboard/timeline`

Returns upcoming hearings/deadlines.

### GET `/api/dashboard/attention`

Returns AI/manual action items needing attention.

## Reports

### POST `/api/reports`

Create report job.

Payload:

```json
{
  "report_type": "case_summary",
  "client_id": "...",
  "case_id": "...",
  "format": "pdf"
}
```

### GET `/api/reports/{job_id}/status`

Poll report job.

### GET `/api/reports/{job_id}/download`

Download report.

## API Response Standards

Every long-running job returns:

```json
{
  "id": "...",
  "status": "pending|processing|success|failed"
}
```

Every AI result should include:

```json
{
  "answer": "...",
  "citations": [],
  "tool_trace": [],
  "confidence": 0.82,
  "metadata": {}
}
```
