# Tech Stack

## Backend-First Recommendation

Use a backend architecture close to EquityNav because the domain structure is similar and the existing patterns are proven:

- FastAPI backend
- SQLAlchemy ORM
- Alembic migrations
- PostgreSQL database
- Background jobs
- SSE/streaming for chat
- Object storage for uploaded documents
- Vector search for RAG
- Structured strategy engine for scenarios

## Recommended Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- Uvicorn

Reason:

EquityNav already uses this style. It is good for API-first SaaS, async background work, typed schemas, and AI service orchestration.

### Database

- Supabase Postgres
- `pgvector`
- JSONB fields for flexible scenario inputs/results
- Row-level ownership enforced at API layer first, optionally Supabase RLS later

Reason:

Supabase is still Postgres. It gives database, storage, auth, and vector capability in one place. We can keep EquityNav-style SQLAlchemy models while using Supabase as the hosted Postgres.

### Auth

Recommended for this project:

- Supabase Auth for MVP

Alternative:

- SuperTokens if we want to copy EquityNav auth architecture more directly.

Recommendation:

Use Supabase Auth unless there is a strong reason to keep SuperTokens. Supabase Auth pairs naturally with Supabase Postgres and Storage.

### Storage

- Supabase Storage for PDFs, images, DOCX, generated reports, and OCR outputs.

Storage buckets:

- `case-documents`
- `draft-exports`
- `report-exports`
- `ocr-artifacts`

### OCR

- ABBYY product/API for scanned legal documents.

Use cases:

- Scanned sale deeds.
- Court orders.
- FIR copies.
- Legal notices.
- Hand-signed affidavits.
- Old judgments.
- Revenue records.

The OCR pipeline should store:

- Original file.
- OCR text.
- Layout metadata when available.
- Extracted structured fields.
- Confidence score.
- Processing status.

### AI/LLM

Use an LLM provider abstraction so models can change later.

Capabilities needed:

- Chat response generation.
- Legal question routing.
- Tool calling.
- Structured extraction.
- Scenario strategy reasoning.
- Draft generation.
- Citation explanation.

### RAG

Recommended:

- Hybrid retrieval.
- Dense vector search using `pgvector`.
- Metadata filtering by country, state, practice area, source type.
- Keyword/BM25 or Postgres full-text search for statutes and sections.
- Re-ranker later if needed.

### External APIs

Useful APIs:

- Indian Kanoon API or alternative legal judgment provider.
- eCourts/Surepass-like API for case status and court metadata.
- Web search API.
- Citation verification provider if available.

Important:

Do not rely only on external APIs. Keep a curated internal legal corpus for core statutes, sections, templates, and common precedents.

### Background Jobs

Options:

- Celery + Redis
- RQ + Redis
- FastAPI background tasks for very early MVP only

Recommendation:

Use Celery/RQ once OCR and embeddings are introduced. For first API skeleton, background task stubs are acceptable.

Jobs needed:

- OCR processing.
- Text extraction.
- Embedding.
- Scenario execution.
- Draft export.
- Research memo generation.
- Report generation.

### Realtime / Streaming

Use:

- Server-Sent Events for chat and long-running jobs.

Same pattern as EquityNav:

- Create message/job.
- Return ID immediately.
- Stream progress/status.
- Persist final answer/result.

### Observability

Minimum:

- Structured logs.
- Request IDs.
- Job IDs.
- Tool-call traces.
- AI cost metadata.

Later:

- PostHog for product analytics.
- Sentry for errors.
- Logfire/OpenTelemetry for traces.

## Suggested Initial Repository Shape

```text
abbyadv/
  docs/
  src/
    main.py
    core/
      config.py
      security.py
      logging.py
    database/
      base.py
      models.py
      crud.py
      vector_store.py
    api/
      deps.py
      routers/
        auth.py
        users.py
        clients.py
        cases.py
        documents.py
        chat.py
        scenarios.py
        drafts.py
        research.py
        dashboard.py
        events.py
        reports.py
      schemas/
        user.py
        client.py
        case.py
        document.py
        chat.py
        scenario.py
        draft.py
        research.py
        event.py
        report.py
    agents/
      chat/
      retrieval/
      legal_engine/
      drafting/
      research/
    services/
      storage.py
      ocr_abbyy.py
      document_processor.py
      embedding_service.py
      citation_service.py
      ecourts_service.py
      indian_kanoon_service.py
      report_service.py
    jobs/
      worker.py
      tasks.py
  alembic/
  tests/
```

## Environment Variables

```text
DATABASE_URL=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=
SUPABASE_STORAGE_BUCKET_CASE_DOCUMENTS=
OPENAI_API_KEY=
ABBYY_API_KEY=
ABBYY_ENDPOINT=
INDIAN_KANOON_API_KEY=
ECOURTS_API_KEY=
SUREPASS_API_KEY=
WEB_SEARCH_API_KEY=
REDIS_URL=
```

## Initial Technical Decisions

- Backend first.
- India-first legal corpus.
- Supabase Postgres as database.
- Supabase Storage for documents.
- SQLAlchemy/Alembic like EquityNav.
- JSONB for flexible scenario payloads.
- Dedicated normalized tables for stable entities.
- Hybrid RAG with metadata filters.
- Tool traces and citations persisted.
