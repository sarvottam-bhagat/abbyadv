# AbbyAdv Backend

FastAPI backend for the advocate workspace, following the EquityNav flow:

`Advocate -> Client -> Case -> Documents / Chat / Scenarios / Drafts / Research`

## Run locally

```powershell
Copy-Item .env.example .env
python -m pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
alembic upgrade head
uvicorn src.main:app
```

Open `http://localhost:8000/docs`. For local development use `DEBUG=true` and `AUTO_CREATE_SCHEMA=true`; requests can use `x-user-id` as a local development identity. In production set `DEBUG=false`, run migrations separately, and provide a Supabase access token in `Authorization: Bearer ...` plus `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, and `DATABASE_URL`.

The local default uses SQLite. Set `DATABASE_URL` to the Supabase Postgres connection string for hosted deployment. Supabase Storage and Qdrant adapters activate automatically when their credentials are configured.

## ABBYY OCR

Set `ABBYY_CLIENT_ID`, `ABBYY_CLIENT_SECRET`, and `ABBYY_SKILL_ID` in `.env`. The document flow follows ABBYY Vantage's single-call workflow for files below 30 MB:

1. `POST /api/documents/{document_id}/process` downloads the stored file, launches an ABBYY transaction, and persists its transaction ID.
2. `GET /api/documents/{document_id}/processing-status` polls ABBYY and downloads result files when processed.
3. Extracted text is chunked, embedded, stored in `document_chunks`, and indexed in Qdrant.

Files at or above 30 MB automatically use ABBYY's separate-call workflow: create transaction, upload file, and start transaction.

## Qdrant RAG

`POST /api/retrieval/search` accepts a query plus optional `case_id` or `document_id`. Every search is filtered by the authenticated `user_id`, and document chunks are indexed with case/document metadata. OpenAI embeddings are used when `OPENAI_API_KEY` is set; a deterministic local embedding fallback keeps development and tests offline.

## MVP flow

1. `POST /api/clients`
2. `POST /api/clients/{client_id}/cases`
3. `POST /api/documents/upload-url`
4. `POST /api/chat`
5. `GET /api/scenarios/types` and `POST /api/scenarios`
6. `POST /api/drafts` / `POST /api/research`
7. `GET /api/dashboard/summary`
