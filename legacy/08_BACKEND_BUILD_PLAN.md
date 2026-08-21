# Backend Build Plan

## Build Philosophy

Backend first. Keep the data model stable. Implement simple CRUD and job flows before deep AI.

Do not start with a complex agent. Start with:

1. Auth/user.
2. Clients.
3. Cases.
4. Documents.
5. Chat persistence.
6. Scenario persistence.
7. Draft/research persistence.
8. Then AI/tool integrations.

## Phase 0: Project Setup

Create backend project:

- FastAPI app
- config management
- database connection
- SQLAlchemy base/models
- Alembic migrations
- API router registration
- basic health endpoint

Deliverables:

- app boots
- DB connects
- migration runs
- `/health` returns ok

## Phase 1: Auth/User Foundation

Implement:

- Supabase JWT verification or temporary dev auth
- `users` model
- `GET /api/me`
- `PATCH /api/me`
- user bootstrap on first authenticated request

Deliverables:

- current user can be resolved
- user profile stored in DB

## Phase 2: Clients

Implement:

- client model
- client schemas
- client CRUD router
- ownership checks
- list/search/filter

Endpoints:

- `POST /api/clients`
- `GET /api/clients`
- `GET /api/clients/{client_id}`
- `PATCH /api/clients/{client_id}`
- `DELETE /api/clients/{client_id}`

Deliverables:

- advocate can manage clients

## Phase 3: Cases

Implement:

- cases model
- case schemas
- cases router
- client ownership validation
- list by client
- search/filter by status/type

Endpoints:

- `POST /api/clients/{client_id}/cases`
- `GET /api/clients/{client_id}/cases`
- `GET /api/cases/{case_id}`
- `PATCH /api/cases/{case_id}`
- `DELETE /api/cases/{case_id}`

Deliverables:

- one client can have multiple cases
- case has jurisdiction/court/stage/hearing fields

## Phase 4: Documents

Implement:

- case_documents model
- document_chunks model
- upload URL endpoint
- document status endpoint
- list documents by case
- process document stub

Endpoints:

- `POST /api/documents/upload-url`
- `POST /api/documents/{document_id}/process`
- `GET /api/documents/{document_id}`
- `GET /api/cases/{case_id}/documents`

Deliverables:

- file metadata and storage key are persisted
- document processing state exists

## Phase 5: Chat Persistence

Implement:

- chat_sessions
- chat_messages
- create chat message endpoint
- session list endpoint
- message status endpoint
- context metadata with client/case/document IDs

Do not build full AI yet. Return a deterministic assistant answer first.

Deliverables:

- chat session created
- user/assistant messages stored
- context attach works

## Phase 6: Scenario Infrastructure

Implement:

- legal_scenarios model
- scenario form schema registry
- scenario create/run endpoint
- strategy registry
- stub strategy outputs
- scenario status/result endpoint

MVP event types:

- land_dispute
- temporary_injunction
- theft_bail
- family_matter
- cheque_bounce
- legal_notice_reply

Deliverables:

- frontend can fetch dynamic forms
- scenario can run and persist structured result

## Phase 7: Drafts And Research Persistence

Implement:

- drafts model/router
- research_memos model/router
- create/list/get/update
- create draft from scenario/research stub

Deliverables:

- draft and research sections can be backed by real API

## Phase 8: Dashboard

Implement summary aggregations:

- total clients
- active cases
- hearings this week
- critical action items
- pending docs
- pending drafts
- matter type breakdown

Deliverables:

- home dashboard can show real data

## Phase 9: OCR Integration

Implement ABBYY service:

- upload/send file
- poll/get result
- store OCR text
- store OCR metadata
- update document status

Then:

- legal field extraction from OCR text
- chunking
- embeddings

Deliverables:

- scanned PDF becomes searchable

## Phase 10: Legal RAG

Implement:

- legal_sources
- legal_source_chunks
- ingestion script
- embedding generation
- retrieval endpoint/service
- metadata filters

Deliverables:

- legal corpus search works
- case doc search works

## Phase 11: Real Chat Agent

Implement:

- context gate
- tool calling
- legal RAG tool
- private document RAG tool
- web search tool
- judgment API tool
- citation verifier tool
- persisted citations/tool trace

Deliverables:

- chat answers with citations using tools

## Phase 12: Real Scenario Strategies

Replace stub strategy results with real strategy agents.

Each strategy should:

- validate inputs
- retrieve sources
- call external tools if required
- generate structured result
- create action items
- recommend drafts/research

Deliverables:

- land dispute and injunction scenarios work end-to-end first

## Phase 13: Reports/Exports

Implement:

- report_jobs
- draft export
- scenario report export
- research memo export

Deliverables:

- downloadable DOCX/PDF artifacts

## Suggested Development Order For Claude Code

1. Scaffold project.
2. Add DB config and models.
3. Add migrations.
4. Add CRUD and routers for users/clients/cases.
5. Add document tables and endpoints.
6. Add chat tables/endpoints.
7. Add scenario tables/registry/stub executor.
8. Add drafts/research/events/dashboard.
9. Add tests.
10. Add AI integrations.

## Initial Test Plan

Unit tests:

- model creation
- ownership validation
- scenario form schemas
- scenario result serialization
- document status transitions

API tests:

- client CRUD
- case CRUD
- chat create/list/status
- scenario create/status/result
- draft CRUD
- research CRUD
- dashboard summary

Integration tests:

- create client -> create case -> upload doc -> create chat -> run scenario.

## Definition Of Backend MVP Complete

Backend MVP is complete when this flow works:

1. User signs in.
2. User creates client.
3. User creates case.
4. User uploads document metadata.
5. User asks chat with client/case attached.
6. User runs scenario.
7. User gets structured result.
8. User creates draft from result.
9. Dashboard reflects upcoming actions.
