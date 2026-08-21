# Product Requirements Document

## Product Name

Working name: **AbbyAdv**

Product category: AI-powered advocate workspace for client, case, document, research, drafting, and scenario management.

## One-Line Idea

AbbyAdv helps advocates manage clients and cases, ask context-aware legal questions, process case documents, research law with citations, generate drafts, and run structured legal scenario analyses.

## Core Analogy From EquityNav

EquityNav is built for CPAs:

`CPA -> Clients -> Equity Grants -> Tax Scenarios -> Chat`

AbbyAdv is built for advocates:

`Advocate -> Clients -> Cases -> Legal Scenarios -> Chat`

The product should feel like a professional workspace, not a generic chatbot. The AI becomes more useful because it can attach the right client, case, documents, court status, laws, judgments, and prior chat context.

## Target User

Primary user:

- Independent advocate
- Small law firm partner/associate
- Litigation-focused lawyer
- Legal assistant or junior advocate working under a senior

Initial jurisdiction:

- India-first MVP.
- Database should support `country` and `jurisdiction` from day one so later USA/UK/Australia/Germany expansion is possible.

## Main User Problems

Advocates often need to:

- Track many clients and cases.
- Remember case facts, document history, hearing dates, next steps, and court stage.
- Read long PDFs, scanned orders, pleadings, notices, FIRs, sale deeds, contracts, and affidavits.
- Find relevant statutes, sections, judgments, and principles.
- Draft notices, replies, applications, arguments, and case notes.
- Prepare for court quickly.
- Avoid missing limitation, evidence gaps, hearing dates, or procedural requirements.
- Reuse knowledge from past matters without manually searching everything.

## Product Promise

AbbyAdv should help the advocate:

- Organize client and case data.
- Ask questions with or without case context.
- Get answers grounded in legal sources and case documents.
- See citations and source references.
- Process scanned legal documents using OCR.
- Generate drafts with matter context.
- Run structured scenario analyses for common legal workflows.
- Track action items, hearings, limitation dates, and missing documents.

## Core Product Sections

### 1. Home Dashboard

Purpose:

Give the advocate a command center for practice activity.

Should show:

- Total clients
- Active cases
- Hearings this week
- Critical action items
- Drafts pending
- Documents pending OCR/review
- Cases needing attention
- Upcoming timeline
- AI-generated alerts
- Matter mix by type: property, criminal, family, commercial, revenue, consumer, labour, etc.

Example AI alerts:

- "Temporary injunction filing needs site photos and certified sale deed."
- "Bail hearing tomorrow. FIR and remand order not uploaded."
- "Cheque bounce notice deadline may expire in 3 days."
- "Family matter mediation note still in draft."

### 2. Clients

Purpose:

Manage the advocate's clients.

Client profile should include:

- Full name
- Email
- Phone
- Address
- City/state/country
- Client type: individual, business, family, trust, government, other
- Status: active, inactive, archived
- Notes
- Tags

Client can have multiple cases.

### 3. Cases

Purpose:

Replace EquityNav's `Grant` concept.

A case is the main legal matter attached to a client.

Case profile should include:

- Case name
- Matter type
- Country
- State
- Court
- Jurisdiction
- Case number/CNR number/FIR number
- Client role
- Opposite party
- Opposite advocate
- Current stage
- Next hearing date
- Limitation date
- Relief sought
- Short facts
- Case status
- Risk level
- Tags

One client can have multiple cases.

### 4. Chat

Purpose:

Main AI assistant for flexible work.

The advocate can ask:

- General legal research questions without attaching anything.
- Client-specific questions using `@client`.
- Case-specific questions using `/case`.
- Document-specific questions after uploading PDFs/images/DOCX.

Chat should support:

- `@` client attach
- `/` case attach
- File upload
- OCR extraction for scanned docs
- RAG over legal corpus
- Retrieval over private case docs
- External API tools
- Web search
- Citations
- Follow-up questions
- Saved conversation sessions

Example questions:

- "What urgent relief should we seek in this land dispute?"
- "Find precedents for temporary injunction where construction started suddenly."
- "Summarize this FIR and identify bail grounds."
- "Draft a reply to this legal notice."
- "What documents are missing before filing?"
- "What questions should I be ready for in court tomorrow?"
- "Compare our facts with the attached judgment."

### 5. Scenarios

Purpose:

Structured legal analysis for common situations, similar to EquityNav tax scenarios.

MVP scenarios:

- Land dispute
- Temporary injunction
- Theft/bail
- Family maintenance/custody
- Cheque bounce
- Legal notice reply

Scenario flow:

1. Select client.
2. Select case.
3. Select event type.
4. Dynamic form opens based on event type.
5. Upload supporting documents.
6. Run scenario.
7. System executes strategy using case facts, documents, legal RAG, external APIs, and LLM.
8. Output structured result.

Scenario output should include:

- Case snapshot
- Legal issue matrix
- Applicable law
- Relevant sections
- Supporting precedents
- Adverse precedents
- Evidence gaps
- Limitation/procedure risks
- Drafting suggestions
- Court preparation questions
- Next action checklist
- Citations

### 6. Drafts

Purpose:

Standalone drafting workspace.

Draft types:

- Legal notice
- Reply notice
- Plaint
- Written statement
- Bail application
- Anticipatory bail application
- Temporary injunction application
- Affidavit
- Evidence affidavit
- Argument note
- Case summary
- Research memo

Drafts can be:

- Created from scratch.
- Created from chat.
- Created from scenario output.
- Linked to client/case.
- Improved with AI.
- Citation-checked.
- Exported as DOCX/PDF.

### 7. Research

Purpose:

Standalone legal research workflow separate from chat.

Research should support:

- Search statutes.
- Search judgments.
- Find precedents.
- Compare cases.
- Explain cited principles.
- Save memo to case.
- Send result to chat.
- Create draft from research.

Sources:

- Internal legal RAG.
- Indian Kanoon API or similar provider.
- eCourts/Surepass-style APIs for case status.
- Web search.
- Case document vault.

## MVP Scope

### Must Have

- Auth and advocate profile.
- Clients CRUD.
- Cases CRUD.
- Document upload and metadata.
- Chat sessions/messages.
- Client/case context attachment in chat.
- Basic legal RAG.
- OCR pipeline stub with ABBYY integration planned.
- Scenario create/run/status/result.
- First 6 scenario types.
- Draft create/list/update.
- Research memo create/list/save.
- Dashboard summary.
- Audit logs.

### Should Have

- Background jobs for OCR, embeddings, scenario runs, and report generation.
- Citation object model.
- Source tracing.
- Document extraction status.
- Case event/hearing timeline.
- Basic report export.

### Later

- Court calendar sync.
- Gmail/Calendar integrations.
- WhatsApp/email drafting.
- Billing/time tracking.
- Multi-country legal packs.
- Team roles and firm workspace.
- Advanced citation verification.

## Success Criteria For MVP

An advocate should be able to:

1. Create a client.
2. Create a case under that client.
3. Upload documents.
4. Ask chat a question with the client and case attached.
5. Receive an answer using case facts, legal sources, and citations.
6. Run a land dispute or bail scenario.
7. Generate a draft from the scenario or chat answer.
8. Save research to the case.
9. See next action items on dashboard.

## Non-Goals For First Backend Milestone

- Full frontend polish.
- Payment billing.
- Multi-country legal expansion.
- Perfect legal database coverage.
- Fully automated legal advice.
- Any feature that makes final legal decisions for the advocate.

## Legal Safety Positioning

The product is an advocate assistant, not a replacement for advocate judgment.

Every answer should:

- Show sources/citations when legal claims are made.
- Distinguish facts from legal inference.
- Flag uncertainty.
- Recommend advocate verification before filing.
- Avoid pretending to be authoritative where source coverage is weak.
