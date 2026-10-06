import logging
from typing import List
from app.models.schemas import (
    ResearchPlan,
    SearchResult,
    EvidenceItem,
    ConflictItem,
    VerificationResult,
    FinalResearchReport
)
from app.services.llm_service import llm_service
from app.agent.prompts import SYNTHESIZER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class ReportSynthesizer:
    def synthesize(
        self,
        plan: ResearchPlan,
        sources: List[SearchResult],
        evidence: List[EvidenceItem],
        conflicts: List[ConflictItem],
        verification: VerificationResult
    ) -> FinalResearchReport:
        """Synthesize verified evidence, conflicts, and sources into a publication-grade research report."""
        logger.info("Synthesizing final research report...")

        # Build clean reference index mapping
        unique_sources = []
        seen_urls = set()
        for s in sources:
            if s.url not in seen_urls:
                seen_urls.add(s.url)
                unique_sources.append(s)

        source_index_map = {}
        references_prompt_lines = []
        for idx, s in enumerate(unique_sources, 1):
            source_index_map[s.url] = idx
            references_prompt_lines.append(f"[{idx}] {s.title} | URL: {s.url} | Snippet: {s.snippet[:140]}")

        # Format verified claims with evidence
        verified_claims_lines = []
        for c in verification.claims_evaluated:
            if c.is_grounded:
                verified_claims_lines.append(f"- Verified Claim: {c.claim_text} (Score: {c.grounding_score})")

        # Format conflicts
        conflicts_lines = []
        for cf in conflicts:
            conflicts_lines.append(
                f"- Conflict on '{cf.topic}': Claim A: '{cf.claim_a}' ({cf.source_a_url}) vs Claim B: '{cf.claim_b}' ({cf.source_b_url}). Cause: {cf.possible_reason}"
            )

        user_prompt = f"""Generate a comprehensive, structured Final Research Report for:

RESEARCH QUESTION: {plan.main_question}
CLARIFIED SCOPE: {plan.clarified_scope}

VERIFIED CLAIMS AND EVIDENCE:
{chr(10).join(verified_claims_lines)}

RAW EVIDENCE ITEMS:
{chr(10).join([f"[{ev.id}] {ev.claim} (Source URL: {ev.source_url}, Quote: '{ev.verbatim_quote}')" for ev in evidence])}

IDENTIFIED CONFLICTS & DISAGREEMENTS:
{chr(10).join(conflicts_lines) if conflicts_lines else "No substantive conflicts identified; evidence is in broad consensus."}

VERIFICATION AUDIT SUMMARY:
Overall Grounding Score: {verification.overall_grounding_score}
Audit Critique: {verification.reflection_critique}

AUTHORIZED REFERENCES TO CITE:
{chr(10).join(references_prompt_lines)}

REPORT REQUIREMENTS:
1. Executive Summary: High-level synthesis with inline citations e.g. [1], [2].
2. Methodology: Explain decomposition, bounded retrieval, and cross-source verification.
3. Key Findings: 3 to 5 discrete findings with headline, detailed evidence explanation, confidence, and source citations matching [index].
4. Comparison Tables: At least one structured comparison table with clear columns and rows comparing entities, chemistry, or trade-offs where applicable.
5. Conflicting Information: Clearly document all identified contradictions without smoothing them over.
6. Limitations: Explicitly state data gaps, unverified claims, or test boundaries.
7. Conclusion: Authoritative strategic conclusion.
8. References: Populate every cited reference with its exact matching citation index [1], [2], title, and URL.
"""

        report = llm_service.generate_structured(
            system_prompt=SYNTHESIZER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=FinalResearchReport,
            temperature=0.2
        )
        return report

synthesizer = ReportSynthesizer()
