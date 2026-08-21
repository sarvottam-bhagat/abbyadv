# Security and Compliance

## Why This Matters

Legal SaaS handles sensitive client information:

- names and addresses
- legal disputes
- FIRs
- contracts
- property records
- family details
- court orders
- privileged communications
- drafts and strategy notes

Security must be designed from day one.

## Data Ownership

Every user-owned record must be scoped to `user_id`.

Rules:

- A user can only access their own clients.
- A user can only access cases under their clients.
- A user can only access documents under their clients/cases.
- AI retrieval must filter by `user_id` and `case_id`.
- External API results saved to a case inherit the same ownership.

## Authentication

Use Supabase Auth or equivalent JWT auth.

Backend must:

- verify JWT signature
- resolve current user
- create local user row if needed
- reject blocked users

## Authorization

Never trust IDs from request payloads.

Before any operation:

- validate client belongs to current user
- validate case belongs to current user
- validate document belongs to current user
- validate scenario/draft/research belongs to current user

## Document Security

Uploaded files should:

- be stored in private bucket
- use signed URLs only
- never be publicly accessible
- have storage key scoped by user/case
- be deleted when user deletes document if required

Recommended storage path:

```text
case-documents/{user_id}/{case_id}/{document_id}/{file_name}
```

## RAG Security

Private document retrieval must always filter by:

- `user_id`
- optionally `client_id`
- optionally `case_id`
- optionally `document_id`

Never allow cross-user vector search leakage.

## AI Safety

Each AI answer should:

- cite sources where possible
- flag uncertainty
- distinguish law, fact, and inference
- avoid guaranteeing outcomes
- remind that advocate must verify before filing

Do not:

- fabricate citations
- expose hidden prompts
- reveal other users' data
- make final legal decisions

## Audit Logs

Add audit logging for:

- login/user bootstrap
- client created/updated/deleted
- case created/updated/deleted
- document uploaded/deleted
- OCR processed
- chat answer generated
- scenario run
- draft generated/exported
- research memo saved

Audit log fields:

- audit_id
- user_id
- entity_type
- entity_id
- action
- metadata_json
- ip_address
- user_agent
- created_at

## Sensitive Data In Logs

Do not log:

- full document text
- full chat prompts
- client private details
- API keys
- signed URLs

Log IDs and metadata only.

## API Key Security

Store keys in environment variables:

- ABBYY key
- OpenAI/LLM key
- Indian Kanoon key
- eCourts/Surepass key
- web search key

Never store API keys in database unless encrypted.

## Rate Limits

Add limits for:

- chat messages per minute
- OCR jobs per hour
- external API calls
- document uploads
- scenario runs

## Data Retention

MVP can keep data until user deletes it.

Later add:

- firm retention policy
- hard delete queue
- export user data
- delete user workspace

## Compliance Position

India-first legal SaaS should consider:

- confidentiality expectations
- IT Act/security practices
- DPDP Act principles
- professional responsibility of advocates

The product should be positioned as:

- productivity assistant
- legal research assistant
- drafting assistant
- case management assistant

Not:

- replacement for advocate
- consumer legal advice bot without lawyer supervision

## Security MVP Checklist

- JWT verification
- ownership checks
- private storage
- signed URLs
- no cross-user vector search
- audit logs
- no sensitive logs
- environment-based secrets
- basic rate limits
- AI citation/uncertainty behavior
