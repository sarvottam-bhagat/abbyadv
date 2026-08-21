# Legal Scenario Engine

## Goal

Build a scenario system similar to EquityNav's tax scenario engine, but for legal workflows.

EquityNav:

```text
event_type -> dynamic form -> strategy mapper -> strategy executor -> structured tax result
```

AbbyAdv:

```text
event_type -> dynamic legal form -> legal strategy -> retrieval/tool calls -> structured legal result
```

## Why Scenarios Exist

Chat is flexible, but advocates often need repeatable structured analysis.

Scenarios are useful when:

- the same legal pattern repeats often
- specific facts must be collected
- output must follow a predictable structure
- the system can create action items/drafts/research from the result

## MVP Scenario Types

### 1. Land Dispute

Inputs:

- property type
- claim basis
- possession status
- date of interference/dispossession
- opposite party claim
- relief sought
- title documents
- revenue records
- photos/site plan

Output:

- title/possession issue matrix
- applicable law
- injunction or declaration recommendation
- limitation risk
- evidence gap checklist
- supporting/adverse cases
- next filing steps

### 2. Temporary Injunction

Inputs:

- subject matter
- immediate threat
- urgency level
- notice status
- relief requested
- prior orders
- documentary support

Output:

- prima facie case analysis
- balance of convenience
- irreparable injury
- ex-parte justification
- draft prayer clauses
- court questions

### 3. Theft / Bail

Inputs:

- alleged sections
- FIR facts
- arrest/custody status
- recovery status
- prior criminal history
- investigation stage
- medical/CCTV/witness docs

Output:

- bail grounds
- adverse facts
- custody timeline
- relevant precedents
- surety checklist
- questions for client
- draft bail application outline

### 4. Family Matter

Inputs:

- proceeding type
- client role
- marriage/relationship facts
- children involved
- income proof
- relief sought
- mediation status

Output:

- relief-wise strategy
- maintenance/custody factors
- documents needed
- settlement points
- draft application/reply outline

### 5. Cheque Bounce

Inputs:

- client side
- cheque amount
- dishonour reason
- notice sent/received date
- delivery proof
- debt/liability proof
- reply status

Output:

- Section 138 ingredient checklist
- limitation timeline
- complaint/reply strategy
- defences and rebuttal points
- document gaps

### 6. Legal Notice Reply

Inputs:

- notice category
- allegations
- demand amount
- deadline
- response tone
- admission risk
- supporting documents

Output:

- allegation-by-allegation response
- admissions to avoid
- counter-claim points
- draft reply outline
- settlement posture

## Strategy File Contract

Each strategy should expose:

```python
EVENT_TYPE = "land_dispute"

def get_form_schema() -> dict:
    ...

async def execute(context: LegalScenarioContext) -> LegalScenarioResult:
    ...
```

## Form Schema Shape

```json
{
  "event_type": "land_dispute",
  "label": "Land Dispute",
  "description": "Analyze title, possession, injunction, limitation, and evidence gaps.",
  "fields": [
    {
      "name": "property_type",
      "label": "Property type",
      "type": "select",
      "required": true,
      "options": [
        {"label": "Residential plot", "value": "residential_plot"}
      ]
    }
  ],
  "document_prompts": [
    "sale_deed",
    "mutation_record",
    "site_photos"
  ],
  "analysis_options": [
    "include_supporting_cases",
    "include_adverse_cases",
    "include_limitation_risk",
    "include_draft_suggestions"
  ]
}
```

## Scenario Context

Strategy receives:

```json
{
  "user": {},
  "client": {},
  "case": {},
  "input_parameters": {},
  "documents": [],
  "retrieved_case_chunks": [],
  "retrieved_legal_sources": [],
  "external_search_results": [],
  "country": "IN",
  "state": "DL"
}
```

## Result Shape

```json
{
  "summary": "...",
  "risk_level": "high",
  "issue_matrix": [],
  "applicable_laws": [],
  "supporting_precedents": [],
  "adverse_precedents": [],
  "evidence_gaps": [],
  "limitation_risks": [],
  "drafting_recommendations": [],
  "court_prep_questions": [],
  "next_actions": [],
  "citations": [],
  "tool_trace": []
}
```

## Execution Steps

1. Validate input parameters.
2. Load client and case.
3. Load selected documents.
4. Retrieve private case chunks.
5. Retrieve legal source chunks using country/state/practice filters.
6. Call external judgment/court APIs if needed.
7. Run strategy prompt/logic.
8. Verify citations.
9. Save result.
10. Create suggested action items/events if configured.

## Strategy vs Chat

Chat:

- flexible
- conversational
- can answer anything

Scenario:

- structured
- repeatable
- produces fixed output sections
- can power reports/drafts/action items

Both should share tools:

- legal RAG
- private document RAG
- external APIs
- citation verifier

## MVP Strategy Outputs By Section

Every scenario should return:

- `case_snapshot`
- `key_questions`
- `applicable_law`
- `facts_needed`
- `documents_needed`
- `supporting_cases`
- `adverse_cases`
- `risk_flags`
- `recommended_next_steps`
- `draft_suggestions`
- `court_questions`

## Action Item Generation

Scenario result can create action items:

- missing document
- urgent filing
- limitation approaching
- hearing preparation
- draft needed
- citation verification needed

Example:

```json
{
  "title": "Collect certified sale deed",
  "priority": "critical",
  "due_date": "2026-07-15",
  "source_type": "scenario",
  "source_id": "scenario_uuid"
}
```

## First Implementation Recommendation

Build scenario infrastructure with stubbed AI first:

1. Form schemas endpoint.
2. Scenario CRUD.
3. Strategy registry.
4. Strategy executor returning deterministic mock result.
5. Persist result.
6. Later plug in retrieval/tools/LLM.

This lets frontend and backend move quickly without blocking on perfect legal AI.
