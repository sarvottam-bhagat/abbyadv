# AbbyAdv Backend Production Runbook

## Required secrets

Set these in the deployment secret manager, never in source control:

```text
DEBUG=false
AUTO_CREATE_SCHEMA=false
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_PUBLISHABLE_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
QDRANT_URL=https://...
QDRANT_API_KEY=...
ABBYY_BASE_URL=https://vantage-au.abbyy.com
ABBYY_CLIENT_ID=...
ABBYY_CLIENT_SECRET=...
ABBYY_SKILL_ID=...
OPENAI_API_KEY=...
```

The service key is server-only. Do not expose it to the frontend or prefix it with a public environment-variable convention.

## Deployment order

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
alembic upgrade head
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

The application refuses production startup when required Supabase configuration is missing. Production does not run `create_all`; schema changes must go through Alembic.

## Supabase verification

After setting `DATABASE_URL`, run the CLI security and performance advisors against the linked project:

```powershell
supabase db advisors --db-url $env:DATABASE_URL --type all --level warn
```

Verify that the private `case-documents` bucket exists and that `storage.objects` policies allow only the authenticated user's auth UUID as the first path segment. The backend stores uploads as `<supabase-auth-user-id>/<case-id>/<file-name>`.

## Readiness checks

- `GET /health` confirms the process is alive.
- `GET /ready` confirms the database connection is usable.
- `X-Request-Id` is returned on every response for tracing.

Live Supabase, Qdrant, ABBYY, and OpenAI checks require the project's actual credentials; local tests use SQLite and mocked external clients.

