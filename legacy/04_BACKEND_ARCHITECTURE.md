# Backend Architecture

## Architecture Goal

Build a backend-first SaaS platform where every major feature is powered by stable entities:

- user
- client
- case
- document
- chat session/message
- legal scenario
- draft
- research memo
- event/action item

The backend should be modular enough that the frontend can be built later without changing the domain model.

## Top-Level Modules

```text
src/
  main.py
  core/
  database/
  api/
  agents/
  services/
  jobs/
```

## Core Backend Flow

### Client/Case Context Flow

1. Advocate creates client.
2. Advocate creates one or more cases under client.
3. Case holds legal facts, jurisdiction, court metadata, and status.
4. Documents are uploaded to case.
5. OCR/extraction creates structured facts.
6. Embeddings allow private case-document retrieval.
7. Chat/scenarios/drafts/research can attach client and case context.

### Chat Flow

1. User sends message.
2. API stores user message.
3. API creates pending assistant message.
4. Background process runs chat agent.
5. Agent decides whether context is needed.
6. Agent loads selected client/case/doc context.
7. Agent calls tools:
   - private case document retrieval
   - legal RAG
   - Indian Kanoon/external judgment API
   - eCourts/Surepass API
   - web search
   - citation verifier
8. Agent streams answer.
9. Final answer, citations, tool trace, and metadata are persisted.

### Document Flow

1. User requests upload URL.
2. File is uploaded to storage.
3. API creates `case_documents` row.
4. OCR job runs if document is scanned/image-heavy.
5. Text extraction job stores extracted text.
6. Structured extraction job stores legal facts.
7. Chunking/embedding job creates `document_chunks`.
8. Document becomes searchable inside chat/scenarios/research.

### Scenario Flow

1. User selects case.
2. User selects scenario event type.
3. Backend returns dynamic form schema.
4. User submits scenario input.
5. API creates scenario row with pending status.
6. Background strategy execution starts.
7. Strategy loads:
   - client profile
   - case profile
   - uploaded docs
   - relevant legal RAG
   - external sources
8. Strategy produces structured result.
9. Result creates optional action items/events/drafts.

### Draft Flow

1. User creates draft manually, from chat, research, or scenario.
2. Draft service loads linked context.
3. Draft agent generates content.
4. Citation service validates citations.
5. Draft is stored as markdown/html.
6. Export job creates DOCX/PDF.

### Research Flow

1. User asks research query.
2. Research service runs legal RAG + external APIs.
3. Answer is generated with citations.
4. User can save memo, attach to case, send to chat, or create draft.

## API Layer

Routers:

- `users.py`
- `clients.py`
- `cases.py`
- `documents.py`
- `chat.py`
- `scenarios.py`
- `drafts.py`
- `research.py`
- `dashboard.py`
- `events.py`
- `reports.py`

Schemas:

- Pydantic create/update/response schemas per module.

Dependencies:

- `get_current_user`
- ownership validators
- database session provider

## Service Layer

Services should contain domain operations that are bigger than CRUD.

Recommended services:

- `storage_service.py`
- `document_processor.py`
- `ocr_abbyy_service.py`
- `embedding_service.py`
- `retrieval_service.py`
- `citation_service.py`
- `chat_service.py`
- `scenario_service.py`
- `draft_service.py`
- `research_service.py`
- `dashboard_service.py`
- `event_service.py`
- `report_service.py`

## Agent Layer

Agents should not directly own database schema logic. They receive structured context and return structured results.

Recommended agents:

- `chat_agent`
- `context_gate`
- `legal_retrieval_agent`
- `scenario_orchestrator`
- `draft_agent`
- `research_agent`
- `citation_verifier_agent`
- `document_extraction_agent`

## Legal Engine

Similar to EquityNav `tax_engine/strategies`.

AbbyAdv should have:

```text
agents/legal_engine/
  registry.py
  orchestrator.py
  executor.py
  explainer.py
  strategies/
    land_dispute.py
    temporary_injunction.py
    theft_bail.py
    family_matter.py
    cheque_bounce.py
    legal_notice_reply.py
```

Each strategy should define:

- supported event type
- dynamic form schema
- required inputs
- optional document types
- retrieval plan
- external tool plan
- result schema
- action item rules

## Context Model

Any AI feature can receive:

```json
{
  "user_id": "...",
  "client_ids": ["..."],
  "case_ids": ["..."],
  "document_ids": ["..."],
  "country": "IN",
  "state": "DL",
  "mode": "chat|scenario|draft|research"
}
```

## RAG Boundaries

Two retrieval layers:

### 1. Legal Corpus RAG

For general legal knowledge:

- statutes
- sections
- rules
- landmark judgments
- templates
- playbooks

### 2. Private Case RAG

For matter-specific facts:

- uploaded documents
- OCR text
- generated summaries
- prior drafts
- prior research memos
- chat context

The answer generator must clearly distinguish:

- "From the case documents..."
- "Under the applicable law..."
- "Based on retrieved precedent..."
- "Inference / strategy suggestion..."

## Background Job Types

- `ocr_document`
- `extract_document_facts`
- `embed_document`
- `run_chat_message`
- `run_legal_scenario`
- `generate_draft`
- `run_research`
- `generate_report`
- `sync_ecourts_status`

## Streaming

Use SSE for:

- chat answers
- scenario progress
- OCR/document processing status
- research progress
- report generation

Example events:

```text
status: loading_case_context
status: searching_legal_sources
status: checking_external_cases
token: ...
status: finalizing_citations
done
```

## Dashboard Aggregation

Dashboard should be read-only aggregation from:

- clients
- cases
- legal_events
- action_items
- case_documents
- drafts
- legal_scenarios

First version can compute live from DB. Later add snapshots/cache.

## Reports

Reports should be async jobs.

Report types:

- client summary
- case summary
- scenario analysis report
- research memo export
- draft export
- hearing preparation bundle

## Error Handling

Each long-running operation should have:

- status
- error message
- retry support
- persisted partial metadata if available

Never lose:

- uploaded document metadata
- user prompt
- scenario input
- failed tool trace

## Ownership Enforcement

Every API must verify:

- current user owns client
- current user owns case
- case belongs to client
- document belongs to case/client/user
- scenario/draft/research belongs to user

Do not trust client-supplied IDs.

## Backend MVP Milestone

First backend milestone is successful when:

- Auth user can be resolved.
- User can CRUD clients.
- User can CRUD cases under clients.
- User can upload document metadata.
- User can create chat session and message.
- User can attach client/case context.
- User can create and run a fake/stub scenario job.
- User can persist scenario result.
- User can create draft/research memo rows.
- Dashboard returns useful counts.
