import logging
from typing import List
from app.models.schemas import EvidenceItem, ConflictItem, VerificationResult, ClaimVerification
from app.services.llm_service import llm_service
from app.agent.prompts import VERIFIER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class ResearchVerifier:
    def verify(
        self,
        question: str,
        evidence: List[EvidenceItem],
        conflicts: List[ConflictItem]
    ) -> VerificationResult:
        """Perform a formal reflection and source grounding verification before synthesis."""
        if not evidence:
            logger.warning("No evidence available for verification.")
            return VerificationResult(
                claims_evaluated=[],
                overall_grounding_score=0.0,
                unsupported_claims_removed_or_flagged=["No primary evidence retrieved to verify."],
                verification_passed=False,
                reflection_critique="Failed verification: Zero empirical evidence items were collected."
            )

        evidence_digest = []
        for ev in evidence:
            evidence_digest.append(
                f"- ID: {ev.id}\n"
                f"  Claim: {ev.claim}\n"
                f"  Source: {ev.source_title} ({ev.source_url})\n"
                f"  Verbatim Proof Quote: \"{ev.verbatim_quote}\"\n"
                f"  Confidence: {ev.confidence_score}\n"
            )
        evidence_str = "\n".join(evidence_digest)

        conflicts_digest = []
        for cf in conflicts:
            conflicts_digest.append(
                f"- Conflict [{cf.id}] on '{cf.topic}': '{cf.claim_a}' vs '{cf.claim_b}' (Severity: {cf.severity})"
            )
        conflicts_str = "\n".join(conflicts_digest) if conflicts_digest else "None identified."

        user_prompt = f"""Conduct a rigorous verification and reflection audit on the research findings gathered for:

Research Question: {question}

EVIDENCE ITEMS TO AUDIT:
{evidence_str}

IDENTIFIED SOURCE DISAGREEMENTS:
{conflicts_str}

VERIFICATION MANDATE:
1. Examine each candidate claim against its verbatim proof quote.
2. Determine if the claim is legitimately grounded in the text or if it represents an unsupported extrapolation or hallucination.
3. Compute the factual grounding score (0.0 to 1.0) for each claim and the overall average.
4. Flag any claims that must be removed or toned down due to weak attribution.
5. Provide a constructive reflection critique noting remaining knowledge gaps and uncertainties.
"""
        logger.info("Executing reflection and verification audit...")
        result = llm_service.generate_structured(
            system_prompt=VERIFIER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=VerificationResult,
            temperature=0.1
        )
        return result

    def verify_single_claim(self, claim_text: str, evidence: List[EvidenceItem]) -> ClaimVerification:
        """Audits an arbitrary single claim against the current evidence pool."""
        evidence_digest = "\n".join([
            f"- [{ev.id}] Quote: \"{ev.verbatim_quote}\" (Source: {ev.source_url})"
            for ev in evidence
        ])
        user_prompt = f"""Verify whether the following claim is strictly grounded in the retrieved quotes:

Claim to Verify: "{claim_text}"

Available Evidence Quotes:
{evidence_digest}

Evaluate grounding, citation fidelity, and assign a grounding score (0.0 to 1.0).
"""
        result = llm_service.generate_structured(
            system_prompt=VERIFIER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ClaimVerification,
            temperature=0.1
        )
        return result

verifier = ResearchVerifier()
