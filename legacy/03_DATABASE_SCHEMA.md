# Database Schema

## Schema Design Principle

Follow EquityNav's shape, adapted to legal workflows.

EquityNav:

```text
users
  -> clients
      -> grants
      -> scenarios
      -> suggestions
      -> equity_events
  -> chat_sessions
      -> chat_messages
```

AbbyAdv:

```text
users
  -> clients
      -> cases
          -> case_documents
          -> legal_scenarios
          -> drafts
          -> research_memos
          -> legal_events
      -> suggestions/action_items
  -> chat_sessions
      -> chat_messages
```

## Entity Mapping From EquityNav

| EquityNav Entity | AbbyAdv Entity | Purpose |
|---|---|---|
| User / CPA | User / Advocate | Owner of workspace |
| Client | Client | Person/business represented |
| Grant | Case / Matter | Main managed object under client |
| Scenario | Legal Scenario | Structured legal analysis |
| ChatSession | ChatSession | Conversation |
| ChatMessage | ChatMessage | User/assistant messages |
| EquityEvent | LegalEvent | Hearings, deadlines, tasks |
| Suggestion | ActionItem/Suggestion | AI/manual next steps |
| PayrollSnapshot | DocumentExtraction | OCR/extracted case facts |
| ReportJob | ReportJob | Generated memo/report/draft export |

## Core Tables

### users

Advocate account/profile.

Columns:

- `user_id uuid primary key`
- `auth_user_id text unique not null`
- `email text not null`
- `full_name text not null`
- `firm_name text null`
- `phone text null`
- `bar_registration_number text null`
- `country text default 'IN'`
- `default_state text null`
- `profile_settings jsonb null`
- `is_blocked boolean default false`
- `blocked_at timestamptz null`
- `created_at timestamptz`
- `updated_at timestamptz`

Relationships:

- one user has many clients
- one user has many chat sessions
- one user has many legal events
- one user has many report jobs

Indexes:

- `auth_user_id`
- `email`

### clients

Client managed by advocate.

Columns:

- `client_id uuid primary key`
- `user_id uuid references users(user_id) on delete cascade`
- `full_name text not null`
- `email text null`
- `phone text null`
- `client_type text not null default 'individual'`
- `address_line_1 text null`
- `address_line_2 text null`
- `city text null`
- `state text null`
- `country text default 'IN'`
- `postal_code text null`
- `status text default 'active'`
- `risk_level text default 'normal'`
- `notes text null`
- `tags jsonb null`
- `metadata_json jsonb null`
- `created_at timestamptz`
- `updated_at timestamptz`

Indexes:

- `user_id`
- `(user_id, status)`
- `(user_id, full_name)`

### cases

Main matter object. This replaces `grants`.

Columns:

- `case_id uuid primary key`
- `client_id uuid references clients(client_id) on delete cascade`
- `user_id uuid references users(user_id) on delete cascade`
- `case_name text not null`
- `matter_type text not null`
- `sub_matter_type text null`
- `country text default 'IN'`
- `state text null`
- `district text null`
- `court_name text null`
- `court_type text null`
- `jurisdiction text null`
- `case_number text null`
- `cnr_number text null`
- `fir_number text null`
- `police_station text null`
- `client_role text null`
- `opposite_party_name text null`
- `opposite_advocate_name text null`
- `current_stage text null`
- `next_hearing_date date null`
- `limitation_date date null`
- `relief_sought text null`
- `facts_summary text null`
- `case_status text default 'active'`
- `risk_level text default 'normal'`
- `tags jsonb null`
- `source_meta jsonb null`
- `scenario_defaults jsonb null`
- `created_at timestamptz`
- `updated_at timestamptz`

Matter types:

- `property`
- `criminal`
- `family`
- `commercial`
- `cheque_bounce`
- `consumer`
- `labour`
- `revenue`
- `constitutional`
- `other`

Indexes:

- `client_id`
- `user_id`
- `(user_id, matter_type)`
- `(user_id, case_status)`
- `next_hearing_date`
- `limitation_date`
- `cnr_number`
- `case_number`

### case_parties

Optional structured party table for complex matters.

Columns:

- `party_id uuid primary key`
- `case_id uuid references cases(case_id) on delete cascade`
- `name text not null`
- `party_type text not null`
- `role text null`
- `contact_json jsonb null`
- `address_json jsonb null`
- `notes text null`
- `created_at timestamptz`
- `updated_at timestamptz`

Party types:

- client
- opposite_party
- witness
- accused
- complainant
- respondent
- petitioner
- court_officer
- other

### case_documents

Uploaded documents linked to client/case.

Columns:

- `document_id uuid primary key`
- `user_id uuid references users(user_id) on delete cascade`
- `client_id uuid references clients(client_id) on delete cascade null`
- `case_id uuid references cases(case_id) on delete cascade null`
- `file_name text not null`
- `file_type text null`
- `mime_type text null`
- `storage_key text not null`
- `storage_bucket text not null`
- `document_type text null`
- `document_date date null`
- `source text default 'upload'`
- `processing_status text default 'uploaded'`
- `ocr_status text default 'not_started'`
- `embedding_status text default 'not_started'`
- `extracted_text text null`
- `summary text null`
- `extracted_facts jsonb null`
- `ocr_metadata jsonb null`
- `page_count int null`
- `confidence_score numeric null`
- `error_message text null`
- `created_at timestamptz`
- `updated_at timestamptz`

Document types:

- sale_deed
- fir
- court_order
- legal_notice
- reply_notice
- plaint
- written_statement
- bail_application
- affidavit
- contract
- invoice
- cheque
- bank_memo
- photo
- judgment
- other

Indexes:

- `user_id`
- `client_id`
- `case_id`
- `processing_status`
- `document_type`

### document_chunks

Chunks for private case-document RAG.

Columns:

- `chunk_id uuid primary key`
- `document_id uuid references case_documents(document_id) on delete cascade`
- `user_id uuid references users(user_id) on delete cascade`
- `client_id uuid null`
- `case_id uuid null`
- `chunk_index int not null`
- `content text not null`
- `content_hash text null`
- `page_start int null`
- `page_end int null`
- `section_title text null`
- `metadata_json jsonb null`
- `embedding vector`
- `created_at timestamptz`

Indexes:

- `document_id`
- `user_id`
- `case_id`
- vector index on `embedding`

### legal_sources

Curated legal corpus for internal RAG.

Columns:

- `source_id uuid primary key`
- `country text not null`
- `state text null`
- `source_type text not null`
- `title text not null`
- `citation text null`
- `authority_level text null`
- `court text null`
- `year int null`
- `practice_area text null`
- `source_url text null`
- `storage_key text null`
- `metadata_json jsonb null`
- `created_at timestamptz`
- `updated_at timestamptz`

Source types:

- statute
- section
- rule
- regulation
- judgment
- template
- playbook
- article

### legal_source_chunks

Chunks for internal legal RAG.

Columns:

- `chunk_id uuid primary key`
- `source_id uuid references legal_sources(source_id) on delete cascade`
- `country text not null`
- `state text null`
- `source_type text not null`
- `practice_area text null`
- `heading text null`
- `content text not null`
- `citation text null`
- `paragraph_number text null`
- `section_number text null`
- `metadata_json jsonb null`
- `embedding vector`
- `created_at timestamptz`

Indexes:

- `country`
- `state`
- `source_type`
- `practice_area`
- `citation`
- vector index on `embedding`

### chat_sessions

Conversation session.

Columns:

- `session_id uuid primary key`
- `user_id uuid references users(user_id) on delete cascade`
- `title text null`
- `context_meta jsonb null`
- `mode text default 'chat'`
- `created_at timestamptz`
- `updated_at timestamptz`

`context_meta` example:

```json
{
  "clients": [{"id": "...", "name": "Rajesh Sharma"}],
  "cases": [{"id": "...", "name": "Land Dispute"}],
  "documents": [{"id": "...", "file_name": "sale_deed.pdf"}]
}
```

### chat_messages

User/assistant messages.

Columns:

- `message_id uuid primary key`
- `session_id uuid references chat_sessions(session_id) on delete cascade`
- `role text not null`
- `content text not null`
- `status text default 'success'`
- `error_message text null`
- `metadata_json jsonb null`
- `tool_trace jsonb null`
- `citations jsonb null`
- `created_at timestamptz`
- `updated_at timestamptz`

Roles:

- user
- assistant
- system
- tool

Statuses:

- pending
- processing
- success
- failed

### legal_scenarios

Structured legal analysis, same pattern as EquityNav scenarios.

Columns:

- `scenario_id uuid primary key`
- `user_id uuid references users(user_id) on delete cascade`
- `client_id uuid references clients(client_id) on delete cascade`
- `case_id uuid references cases(case_id) on delete set null`
- `name text not null`
- `description text null`
- `country text default 'IN'`
- `state text null`
- `scenario_type text not null`
- `event_type text not null`
- `input_parameters jsonb null`
- `uploaded_document_ids jsonb null`
- `result jsonb null`
- `execution_status text default 'pending'`
- `error_message text null`
- `tool_trace jsonb null`
- `citations jsonb null`
- `is_template boolean default false`
- `created_at timestamptz`
- `updated_at timestamptz`

Scenario event types:

- land_dispute
- theft_bail
- family_matter
- cheque_bounce
- temporary_injunction
- legal_notice_reply

Statuses:

- pending
- processing
- success
- failed

### drafts

Generated or manually created legal drafts.

Columns:

- `draft_id uuid primary key`
- `user_id uuid references users(user_id) on delete cascade`
- `client_id uuid references clients(client_id) on delete set null`
- `case_id uuid references cases(case_id) on delete set null`
- `scenario_id uuid references legal_scenarios(scenario_id) on delete set null`
- `title text not null`
- `draft_type text not null`
- `status text default 'draft'`
- `content_md text null`
- `content_html text null`
- `source_prompt text null`
- `input_context jsonb null`
- `citations jsonb null`
- `version int default 1`
- `created_at timestamptz`
- `updated_at timestamptz`

Draft types:

- legal_notice
- reply_notice
- plaint
- written_statement
- bail_application
- anticipatory_bail
- injunction_application
- affidavit
- argument_note
- research_memo

### research_memos

Saved legal research output.

Columns:

- `memo_id uuid primary key`
- `user_id uuid references users(user_id) on delete cascade`
- `client_id uuid references clients(client_id) on delete set null`
- `case_id uuid references cases(case_id) on delete set null`
- `title text not null`
- `query text not null`
- `answer text null`
- `research_type text null`
- `sources jsonb null`
- `citations jsonb null`
- `tool_trace jsonb null`
- `status text default 'success'`
- `created_at timestamptz`
- `updated_at timestamptz`

### legal_events

Hearings, limitation dates, document deadlines, tasks.

Columns:

- `event_id uuid primary key`
- `user_id uuid references users(user_id) on delete cascade`
- `client_id uuid references clients(client_id) on delete cascade null`
- `case_id uuid references cases(case_id) on delete cascade null`
- `event_type text not null`
- `source text not null`
- `severity text null`
- `title text not null`
- `description text null`
- `start_date date not null`
- `end_date date null`
- `status text default 'active'`
- `is_reviewed boolean default false`
- `reviewed_at timestamptz null`
- `metadata_json jsonb null`
- `created_at timestamptz`
- `updated_at timestamptz`

Event types:

- hearing
- limitation_deadline
- filing_deadline
- document_missing
- scenario_alert
- draft_due
- client_followup
- court_order_review

Sources:

- manual
- system
- scenario
- chat
- ecourts_api

Severity:

- critical
- high
- medium
- low
- info

### action_items

Persisted AI/manual suggestions.

Columns:

- `action_item_id uuid primary key`
- `user_id uuid references users(user_id) on delete cascade`
- `client_id uuid references clients(client_id) on delete cascade null`
- `case_id uuid references cases(case_id) on delete cascade null`
- `source_type text null`
- `source_id uuid null`
- `title text not null`
- `description text null`
- `next_step text null`
- `priority text default 'medium'`
- `status text default 'active'`
- `due_date date null`
- `tags jsonb null`
- `created_at timestamptz`
- `updated_at timestamptz`

### report_jobs

Async report/draft export jobs.

Columns:

- `job_id uuid primary key`
- `user_id uuid references users(user_id) on delete cascade`
- `client_id uuid references clients(client_id) on delete set null`
- `case_id uuid references cases(case_id) on delete set null`
- `job_type text not null`
- `status text default 'pending'`
- `input_payload jsonb null`
- `result_payload jsonb null`
- `storage_key text null`
- `file_name text null`
- `error_message text null`
- `created_at timestamptz`
- `updated_at timestamptz`

## Citation Object Shape

Store citations as JSONB in chat messages, scenarios, drafts, and research memos.

```json
{
  "id": "cit_1",
  "source_type": "judgment",
  "title": "Dalpat Kumar v. Prahlad Singh",
  "citation": "1992 1 SCC 719",
  "court": "Supreme Court of India",
  "year": 1992,
  "url": "https://...",
  "paragraph": "5",
  "quoted_text": "short excerpt only",
  "principle": "Temporary injunction requires prima facie case, balance of convenience, and irreparable injury.",
  "relevance": "high",
  "verified": true
}
```

## Tool Trace Object Shape

```json
[
  {
    "tool": "legal_rag",
    "status": "success",
    "query": "temporary injunction land dispute",
    "result_count": 8,
    "latency_ms": 430
  },
  {
    "tool": "indian_kanoon_search",
    "status": "success",
    "query": "Order 39 land construction injunction",
    "result_count": 5,
    "latency_ms": 1100
  }
]
```

## Multi-Tenant Ownership Rule

Every user-owned table should include `user_id` directly unless it is always reachable through a parent with strict ownership checks.

For safety and easier queries, include `user_id` on:

- cases
- documents
- scenarios
- drafts
- research_memos
- legal_events
- action_items
- report_jobs

## First Migration Order

1. users
2. clients
3. cases
4. case_parties
5. case_documents
6. document_chunks
7. legal_sources
8. legal_source_chunks
9. chat_sessions
10. chat_messages
11. legal_scenarios
12. drafts
13. research_memos
14. legal_events
15. action_items
16. report_jobs
