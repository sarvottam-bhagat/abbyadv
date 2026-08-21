# AbbyAdv / AdvocateAssistant Backend Docs

This folder contains the first-pass product and backend planning docs for the actual AdvocateAssistant app.

The backend will follow the same mental model as EquityNav:

- EquityNav: `CPA -> Client -> Grant -> Scenario -> Chat -> Events -> Reports`
- AbbyAdv: `Advocate -> Client -> Case -> Legal Scenario -> Chat -> Events/Hearings -> Drafts/Research/Reports`

## Documents

1. `01_PRD.md` - product requirements and MVP scope.
2. `02_TECH_STACK.md` - recommended stack for backend-first build.
3. `03_DATABASE_SCHEMA.md` - Postgres schema mapped from EquityNav concepts.
4. `04_BACKEND_ARCHITECTURE.md` - backend modules, services, jobs, and boundaries.
5. `05_API_SPEC.md` - first API surface for backend implementation.
6. `06_AI_RAG_AND_TOOLS.md` - chat agent, legal RAG, citation flow, OCR, and external APIs.
7. `07_SCENARIO_ENGINE.md` - legal scenario engine, dynamic forms, and strategy outputs.
8. `08_BACKEND_BUILD_PLAN.md` - practical phase-by-phase backend build plan.
9. `09_SECURITY_AND_COMPLIANCE.md` - legal SaaS privacy, audit, and safety requirements.

## MVP Principle

Build the backend first around stable entities:

`User`, `Client`, `Case`, `Document`, `ChatSession`, `ChatMessage`, `Scenario`, `Draft`, `ResearchMemo`, `Event`, `ReportJob`.

Once these are stable, the frontend can be added using the same flow we prototyped:

Home, Chat, Clients, Cases, Scenarios, Drafts, Research.
