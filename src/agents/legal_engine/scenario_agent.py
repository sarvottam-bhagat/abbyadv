"""Document-grounded legal scenario analysis without vector retrieval.

Scenario uploads are deliberately small for the MVP. ABBYY extracts their
text, and this agent sends that direct evidence together with the structured
case intake to the selected practice-area profile.
"""
from __future__ import annotations

import json
from typing import Any

from src.agents.legal_engine.registry import STRATEGIES
from src.services.llm import LLMService


class ScenarioAnalysisAgent:
    def __init__(self) -> None:
        self.llm = LLMService()

    async def analyze(
        self,
        event_type: str,
        input_parameters: dict[str, Any],
        case_context: dict[str, Any],
        document_context: list[dict[str, str]],
    ) -> dict[str, Any]:
        strategy = STRATEGIES.get(event_type)
        if strategy is None:
            raise ValueError("Unsupported legal scenario type")

        baseline = strategy.execute(input_parameters)
        evidence = "\n\n".join(
            f"--- Document: {item['file_name']} ---\n{item['text']}"
            for item in document_context
        ) or "No documents were uploaded. Base the review only on the intake form and case metadata."
        prompt = (
            "Prepare a detailed India-focused ADVOCATE WORK PRODUCT for this exact matter, written the way a "
            "senior advocate would brief the client's own case for filing. This is not a neutral summary or a "
            "generic checklist: argue the client's position as persuasively as the record allows, while staying "
            "strictly honest about what is proven, inferred, or missing. Read every supplied fact and ABBYY "
            "document extract, reconcile them, and make the analysis specific to the client, property/incident, "
            "parties, dates, amounts, and documents actually provided.\n\n"
            "EVIDENCE DISCIPLINE:\n"
            "- Use only supplied intake, case metadata, and ABBYY text for factual assertions.\n"
            "- Cite document-backed points inline using [Document: exact file name]. If a fact comes only from the form, say 'Intake states'.\n"
            "- Separate a proven/document-backed fact from an inference and from a missing fact.\n"
            "- ABBYY can contain OCR errors: flag any ambiguous name, number, date, survey number, or clause instead of guessing.\n"
            "- Do not invent documents, statutory sections, judgments, dates, monetary figures, or outcome predictions.\n"
            "- If no legal research source was supplied, describe legal issues and procedural questions without fabricating citations.\n\n"
            "Return ONLY one valid JSON object with these keys:\n"
            "summary (2-4 sentence executive case position, argued from the client's side);\n"
            "case_intake ({practice_area, facts_provided, missing_intake_fields});\n"
            "factual_findings (array of 4-8 substantive, fact-specific findings);\n"
            "key_issues (array of 3-6 issue analyses, each 2-4 sentences);\n"
            "fact_evidence_matrix (array of 6-12 objects, each {fact, source, status}, where fact is one specific, "
            "matter-relevant factual assertion, source is the exact document name in [Document: ...] form or "
            "'Intake states' or 'Not yet supplied', and status is exactly one of 'proven', 'inferred', or 'missing'; "
            "this is the advocate's master fact/evidence table and must not duplicate factual_findings verbatim);\n"
            "issue_analysis (array of 3-6 objects, one per legal issue actually raised by this matter, each "
            "{issue, facts, applicable_law, application, conclusion}: issue names the precise legal question; facts "
            "states only the facts bearing on that issue with [Document: ...] citations where available; "
            "applicable_law names the relevant statute/provision/legal principle without fabricating citations if "
            "none were supplied, and says so plainly if research material is absent; application argues how the "
            "facts satisfy or fail that law issue-by-issue, advocate-style; conclusion states the client's position "
            "on that issue in one or two sentences);\n"
            "evidence_assessment (array explaining what each important document proves, limitations, and verification needed);\n"
            "missing_evidence (specific missing document/fact + why it matters + how to obtain it);\n"
            "timeline_builder (array of {event, date}, including known dates and clearly labelled unknown milestones);\n"
            "strength_analysis ({potential_strengths: detailed array, risks_or_uncertainties: detailed array, readiness});\n"
            "opponent_arguments (array of realistic arguments tied to this matter and a short response/mitigation);\n"
            "opponent_rebuttal (array of 3-6 objects, each {opponent_argument, our_rebuttal, supporting_facts}: "
            "opponent_argument states the single strongest realistic argument the opposite side would raise on that "
            "point; our_rebuttal is the advocate's direct, fact-based counter-argument defending the client, not a "
            "hedge; supporting_facts lists the specific facts/documents that back the rebuttal, or says what is "
            "missing to support it);\n"
            "recommended_reliefs (array of relief + factual basis + any condition/qualification);\n"
            "next_steps (ordered, practical advocate actions for the next 24 hours / 7 days / before filing);\n"
            "filing_readiness ({status, before_filing});\n"
            "filing_checklist (array of 5-10 objects, each {item, status, note}: item is one concrete pre-filing "
            "task specific to this matter such as verifying limitation, completing a title/encumbrance search, "
            "certifying a document, or securing a missing record; status is exactly one of 'done', 'pending', or "
            "'blocked' based on what the record shows; note explains what is blocking it or what remains, or is "
            "empty string if none);\n"
            "missing_inputs; confidence; disclaimer.\n\n"
            "Never use generic phrases such as 'title chain' or 'payment proof' without connecting them to this record. "
            "Every list item must add material, matter-specific value. Do not let fact_evidence_matrix, issue_analysis, "
            "opponent_rebuttal, or filing_checklist merely restate factual_findings/key_issues/opponent_arguments/"
            "next_steps in different words — each must contribute its own distinct structure and content.\n\n"
            f"Practice area: {strategy.label}\n"
            f"Practice-area checklist baseline: {json.dumps(baseline, default=str)}\n\n"
            f"Scenario form: {json.dumps(input_parameters, default=str)}\n\n"
            f"Case metadata: {json.dumps(case_context, default=str)}\n\n"
            f"ABBYY extracted evidence:\n{evidence[:120000]}"
        )
        answer = await self.llm.complete(self._system_prompt(), prompt, json_object=True)
        parsed = self._parse(answer)
        if parsed is None:
            baseline["analysis_note"] = "The AI response could not be structured; review the uploaded ABBYY-extracted documents manually."
            return baseline
        return self._merge_with_baseline(parsed, baseline)

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are AbbyAdv's senior advocate-analyst for Indian legal practice, briefing the case the way a "
            "seasoned advocate would prepare it for the client's own file—not generic consumer advice and not a "
            "neutral third-party summary. Argue the client's position with conviction wherever the record supports "
            "it, build a fact/evidence matrix, apply the law issue-by-issue, anticipate and rebut the opponent's "
            "strongest arguments, and convert the record into a concrete filing checklist. At the same time, be "
            "rigorously honest: separate proven fact from inference from gap, flag OCR ambiguity, and never "
            "fabricate authorities, citations, or factual support. Precision and advocacy discipline both matter—"
            "an advocate who overclaims loses credibility with the court as fast as one who underclaims loses the case."
        )

    @staticmethod
    def _parse(answer: str) -> dict[str, Any] | None:
        candidate = answer.strip()
        if candidate.startswith("```"):
            candidate = candidate.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, dict) else None

    @staticmethod
    def _merge_with_baseline(result: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
        # Preserve a stable response contract even when the model omits a section.
        for key, fallback in baseline.items():
            if key not in result or result[key] in (None, "", [], {}):
                result[key] = fallback
        result["confidence"] = min(max(float(result.get("confidence", baseline["confidence"])), 0.0), 1.0)
        result["disclaimer"] = baseline["disclaimer"]
        return result
