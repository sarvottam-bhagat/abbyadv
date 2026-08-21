# AI, RAG, OCR, Citations, and Tools

## Goal

The app should not be a simple wrapper around an LLM. It should be a legal assistant that uses:

- advocate's client/case data
- uploaded case documents
- OCR extraction
- internal legal RAG
- external legal APIs
- web search
- citation verification
- scenario-specific strategy logic

## AI Modes

### 1. General Chat

No client/case attached.

Used for:

- general law questions
- quick research
- draft ideas
- statute explanation
- precedent search

### 2. Context-Aware Chat

Client and case attached.

Used for:

- case strategy
- document-specific analysis
- draft improvement
- hearing preparation
- evidence gap review

### 3. Document Chat

Uploaded document attached.

Used for:

- summarize PDF
- extract parties/dates/clauses
- compare two documents
- identify missing annexures
- ask questions from FIR/order/notice/deed

### 4. Scenario Agent

Structured workflow.

Used for:

- run land dispute strategy
- run bail strategy
- run cheque bounce timeline
- run family matter analysis
- run injunction matrix

### 5. Draft Agent

Used for:

- generate legal notice
- reply to notice
- application drafting
- argument note
- affidavit
- court prep note

### 6. Research Agent

Used for:

- precedent search
- statutory interpretation
- compare judgments
- save research memo
- create citation-backed summary

## RAG Data Layers

### Layer 1: Internal Curated Legal Corpus

This is the data we should embed/index ourselves.

For India MVP:

- Constitution basics relevant to litigation
- CPC
- CrPC/BNSS depending target legal framework
- IPC/BNS depending target legal framework
- Indian Evidence Act/BSA depending target legal framework
- Transfer of Property Act
- Specific Relief Act
- Registration Act
- Indian Stamp Act
- Limitation Act
- Indian Contract Act
- Indian Easements Act
- Hindu personal law basics
- Muslim personal law basics
- NI Act Section 138 basics
- Family court procedural basics
- Common legal templates
- Scenario playbooks
- Curated landmark judgments

Important:

Do not ingest random unverified data. Start curated.

### Layer 2: Private Case Document Corpus

User-uploaded matter documents:

- sale deeds
- FIRs
- notices
- replies
- court orders
- pleadings
- contracts
- affidavits
- photos metadata
- judgments uploaded by user

This layer must be filtered by:

- user_id
- client_id
- case_id
- document_id

### Layer 3: External Live Sources

Use APIs/tools when current or broad search is needed:

- Indian Kanoon or similar judgment search API
- eCourts/Surepass case status APIs
- web search API
- citation verifier

## Retrieval Approach

Use hybrid retrieval:

1. Query understanding.
2. Determine jurisdiction filters:
   - country
   - state
   - court
   - matter type
   - source type
3. Search private case docs if client/case attached.
4. Search internal legal corpus.
5. Call external APIs if needed.
6. Re-rank/score results.
7. Generate answer with citations.

## Metadata Filters

Every legal source chunk should have:

- country
- state
- source_type
- practice_area
- court
- authority_level
- year
- citation
- section_number
- act_name

Every private case chunk should have:

- user_id
- client_id
- case_id
- document_id
- document_type
- page_start
- page_end

## Chat Agent Tool Set

The chat agent should have these tools:

### `get_client_context`

Loads selected client data.

### `get_case_context`

Loads selected case/matter facts.

### `retrieve_case_documents`

Searches uploaded case docs.

### `retrieve_legal_sources`

Searches internal legal corpus.

### `search_judgments`

Calls Indian Kanoon or another judgment API.

### `get_court_case_status`

Calls eCourts/Surepass-like API if CNR/case number is available.

### `web_search`

Searches web for current legal updates or source lookup.

### `verify_citations`

Checks citations before final answer.

### `draft_document`

Creates a draft when user requests drafting.

### `create_action_item`

Creates follow-up task/deadline.

## Context Gate

Borrow EquityNav's context gate idea.

If the user asks a question without explicit context:

- If session already has client/case attached, classify whether the question needs that context.
- If yes, use session context.
- If no, answer generally.

Examples:

- "What does Order 39 require?" -> general legal answer.
- "Do we have enough documents to file?" -> needs attached case context.
- "Draft this based on our facts" -> needs case/document context.

## OCR With ABBYY

Use ABBYY when:

- file is scanned PDF
- image document
- low text extraction quality
- layout/table extraction matters
- handwritten/signature pages need detection

ABBYY pipeline:

1. Upload original file.
2. Create document row.
3. Send file to ABBYY.
4. Receive OCR text/layout.
5. Store OCR artifact.
6. Run legal field extraction.
7. Chunk and embed.
8. Mark document searchable.

Extracted fields by document type:

### Sale Deed

- parties
- property description
- consideration amount
- registration date
- stamp details
- boundaries
- title transfer clauses

### FIR

- FIR number
- police station
- sections
- accused
- complainant
- incident date/time
- allegations
- witnesses

### Legal Notice

- sender
- recipient
- demand amount
- alleged breach
- deadline
- threatened action

### Court Order

- court
- judge
- case number
- order date
- operative directions
- next date
- compliance requirements

## Citation Strategy

Every legal answer should cite sources when making legal claims.

Citation object should include:

- title
- citation
- court/source
- year
- paragraph/section
- source URL if available
- principle
- relevance
- verified flag

Answer style:

- Main conclusion first.
- Legal basis with citations.
- Case facts application.
- Risks/uncertainties.
- Next steps.

## What Not To Do

- Do not fabricate citations.
- Do not cite without storing source metadata.
- Do not mix user-uploaded facts with law without clearly labeling them.
- Do not give final legal decisions as if replacing the advocate.
- Do not rely only on model memory.

## Legal Corpus MVP

Start with:

- Core bare acts and selected sections.
- 100-300 curated landmark/relevant judgments for MVP practice areas.
- 20-50 drafting templates.
- 6 scenario playbooks.

Practice areas:

- property disputes
- temporary injunction
- theft/bail
- family maintenance/custody
- cheque bounce
- legal notice replies

## Answer Contract

Each AI answer should return:

```json
{
  "answer": "...",
  "citations": [],
  "tool_trace": [],
  "confidence": 0.0,
  "follow_up_questions": [],
  "action_items": [],
  "metadata": {
    "used_client_context": true,
    "used_case_context": true,
    "used_private_documents": true,
    "used_external_search": true
  }
}
```

## MVP Tool Priority

1. Internal legal RAG.
2. Private case document RAG.
3. ABBYY OCR.
4. Indian Kanoon-style search.
5. Web search.
6. eCourts/Surepass case status.
7. Citation verifier.

## Long-Term Advantage

The product becomes stronger over time because the advocate's private case workspace creates structured context:

- documents
- facts
- prior arguments
- drafts
- research memos
- court events
- action items

This makes AbbyAdv more powerful than a generic legal chatbot.
