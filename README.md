# AbbyAdv

AbbyAdv is a full-stack workspace for advocates and legal teams. It brings client records, case management, legal documents, contextual chat, scenario analysis, drafting, research, reports, and deadlines into one application.

The project is designed around a simple workflow:

`Advocate → Client → Case → Documents, Chat, Scenarios, Drafts, Research, and Reports`

## What the project does

AbbyAdv helps an advocate move from an incoming client to an organized case workspace:

1. Create a client and record their contact and legal profile.
2. Open one or more cases for that client.
3. Add parties, important dates, action items, and documents to a case.
4. Process documents with OCR and index their contents for retrieval.
5. Ask questions through case-aware chat and search the document knowledge base.
6. Run legal scenarios, create drafts, perform research, and generate case reports.
7. Track the overall workload from the dashboard.

## Key features

- **Client and case management** — maintain client profiles, matters, parties, hearing dates, limitation dates, and case status.
- **Document workspace** — upload, classify, process, and retrieve case documents.
- **OCR processing** — use ABBYY Vantage to extract text from uploaded files.
- **Knowledge retrieval** — chunk and embed document text for filtered semantic search with Qdrant.
- **Contextual legal chat** — create sessions, attach documents, and stream case-aware responses.
- **Scenario analysis** — run matter-specific workflows and store results for each case.
- **Drafting tools** — generate, review, improve, upload, and export legal drafts.
- **Research workspace** — create and retrieve research memos linked to a case.
- **Reports and planning** — generate case reports and track events and action items.
- **Developer-friendly API** — FastAPI provides interactive OpenAPI documentation out of the box.

## Architecture and technology

| Layer | Technology |
| --- | --- |
| Web application | React 19, TypeScript, Vite, React Router |
| API | FastAPI, Pydantic |
| Data access | SQLAlchemy async, Alembic |
| Local database | SQLite |
| Hosted database and authentication | PostgreSQL and Supabase |
| File storage | Supabase Storage |
| OCR | ABBYY Vantage |
| Embeddings and AI | OpenAI, with an offline deterministic embedding fallback for development |
| Vector retrieval | Qdrant |
| Tests | Pytest, Pytest Asyncio, Vitest |

The React application calls the FastAPI service under `/api`. The API applies user ownership checks before reading or changing client, case, document, and workspace data. In local debug mode, requests can use an `X-User-Id` header. Production requests use Supabase bearer tokens.

## API overview

The tables below show the main API groups. After starting the backend, use [Swagger UI](http://localhost:8000/docs) or [ReDoc](http://localhost:8000/redoc) for complete request bodies, response schemas, and live testing.

| Area | Representative endpoints | Purpose |
| --- | --- | --- |
| Service status | `GET /health`, `GET /ready` | Check the API process and database readiness. |
| Current user | `GET /api/me`, `PATCH /api/me` | Read or update the authenticated user profile. |
| Clients | `POST /api/clients`, `GET /api/clients`, `GET/PATCH/DELETE /api/clients/{client_id}` | Manage client records. |
| Cases | `POST/GET /api/clients/{client_id}/cases`, `GET/PATCH/DELETE /api/cases/{case_id}` | Manage matters belonging to a client. |
| Case parties | `POST/GET /api/cases/{case_id}/parties` | Store people and organizations involved in a case. |
| Documents | `POST /api/documents/upload-url`, `GET /api/cases/{case_id}/documents`, `GET /api/documents/{document_id}` | Create uploads and browse case documents. |
| Document processing | `POST /api/documents/{document_id}/process`, `GET /api/documents/{document_id}/processing-status` | Start OCR/indexing and monitor its status. |
| Knowledge base | `GET /api/knowledge-base/documents`, `POST /api/retrieval/search` | Browse and semantically search indexed material. |
| Chat | `POST /api/chat`, `POST /api/chat/stream`, `GET /api/chat/sessions` | Ask questions, stream answers, and manage chat sessions. |
| Chat attachments | `POST /api/chat/attachments/upload-url`, `POST /api/chat/attachments/complete` | Add documents directly to a chat workflow. |
| Scenarios | `GET /api/scenarios/types`, `POST /api/scenarios`, `GET /api/scenarios/{scenario_id}` | Run and retrieve legal scenario analyses. |
| Drafts | `POST /api/drafts/generate`, `POST /api/drafts/review`, `POST /api/drafts/{draft_id}/improve` | Generate, review, and improve drafts. |
| Draft exports | `GET /api/drafts/{draft_id}/export` | Download a generated draft. |
| Research | `POST /api/research`, `GET /api/research/{memo_id}`, `GET /api/research/case/{case_id}` | Create and retrieve legal research memos. |
| Events | `POST /api/events`, `GET /api/events` | Track hearings, deadlines, and other legal events. |
| Action items | `POST /api/action-items`, `GET /api/action-items`, `PATCH /api/action-items/{item_id}` | Track tasks and their completion state. |
| Reports | `POST /api/reports`, `GET /api/reports/{job_id}/status`, `GET /api/reports/{job_id}/download` | Generate and retrieve case reports. |
| Dashboard | `GET /api/dashboard/summary` | Return an overview of the advocate's workload. |

## Run locally

### Prerequisites

Install the following tools:

- Git
- Python 3.11 or newer
- Node.js 20 LTS or newer, with npm

SQLite is used by default, so PostgreSQL, Supabase, Qdrant, ABBYY, and OpenAI are not required to start the basic local application.

### 1. Clone the repository

```bash
git clone https://github.com/sarvottam-bhagat/abbyadv.git
cd abbyadv
```

### 2. Set up the backend

Create a Python virtual environment.

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

The example configuration enables debug mode and uses a local SQLite database. Apply the database migrations and start the API:

```bash
alembic upgrade head
uvicorn src.main:app --reload
```

The backend is now available at:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`
- Readiness check: `http://localhost:8000/ready`

### 3. Set up the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

For local demo mode, create `frontend/.env.local` with only the backend URL:

```dotenv
VITE_API_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

Open `http://localhost:5173`. When Supabase variables are not configured, the development frontend uses demo mode and sends the local development identity expected by the debug backend.

## Environment configuration

Never commit `.env` or `frontend/.env.local`. Both should contain only local or deployment-specific values.

### Backend variables

| Variables | Purpose |
| --- | --- |
| `APP_NAME`, `DEBUG`, `AUTO_CREATE_SCHEMA`, `CORS_ORIGINS` | Application behavior and allowed web origins. |
| `DATABASE_URL` | Async SQLAlchemy connection URL. SQLite works locally; PostgreSQL is recommended for hosted environments. |
| `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET` | Hosted authentication, user verification, and storage access. |
| `UPLOAD_BUCKET` | Supabase Storage bucket used for case files and generated output. |
| `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION` | Vector database connection and collection name. |
| `OPENAI_API_KEY`, `OPENAI_EMBEDDING_MODEL` | AI and embedding configuration. |
| `ABBYY_BASE_URL`, `ABBYY_CLIENT_ID`, `ABBYY_CLIENT_SECRET`, `ABBYY_SKILL_ID` | ABBYY Vantage OCR connection. |
| `ABBYY_POLL_INTERVAL_SECONDS`, `ABBYY_POLL_TIMEOUT_SECONDS` | OCR polling frequency and timeout. |
| `INDIAN_KANOON_API_TOKEN`, `ECOURTS_API_KEY` | Optional legal research and court-data services. |

### Frontend variables

| Variable | Purpose |
| --- | --- |
| `VITE_API_URL` | FastAPI base URL. Defaults to `http://localhost:8000`. |
| `VITE_SUPABASE_URL` | Supabase project URL for hosted authentication. |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Browser-safe Supabase publishable key. |

For production, set `DEBUG=false`, configure PostgreSQL and Supabase, run Alembic migrations before starting the API, and provide the frontend with the matching Supabase project values.

## Document processing and retrieval

When ABBYY is configured, document processing follows this flow:

1. The client requests an upload URL and uploads the file to storage.
2. `POST /api/documents/{document_id}/process` starts an ABBYY transaction.
3. The processing-status endpoint polls ABBYY and downloads the completed result.
4. Extracted text is split into chunks and stored with document and case metadata.
5. Embeddings are indexed in Qdrant for user-scoped semantic retrieval.

Files under 30 MB use ABBYY's single-call workflow. Larger files use its create, upload, and start transaction workflow.

If `OPENAI_API_KEY` is absent, development and tests use a deterministic local embedding fallback. Qdrant and hosted storage features require their corresponding services when those paths are exercised.

## Tests and verification

Run backend tests from the repository root:

```bash
python -m pytest -q
```

Run frontend tests, type checking, and a production build:

```bash
cd frontend
npm test -- --run
npm run lint
npm run build
```

## Project structure

```text
abbyadv/
├── alembic/              # Database migrations
├── frontend/             # React and TypeScript web application
├── src/
│   ├── agents/           # Chat, retrieval, drafting, research, and scenario workflows
│   ├── api/              # FastAPI routers, dependencies, and request/response schemas
│   ├── core/             # Settings and logging
│   ├── database/         # SQLAlchemy engine, models, and CRUD helpers
│   └── services/         # Storage, OCR, embeddings, retrieval, and external integrations
├── .env.example          # Backend configuration template
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
└── README.md
```

## Security notes

- Keep service-role keys, API tokens, database passwords, and `.env` files out of Git.
- Use the `X-User-Id` development identity only while `DEBUG=true`.
- Use verified Supabase bearer tokens in production.
- Keep ownership filtering in place for all user, client, case, document, and retrieval operations.
- Run database migrations separately during deployment instead of relying on automatic schema creation.

## License

No license has been added yet. Until one is provided, the repository is not automatically licensed for reuse or redistribution.
