import logging
from typing import List
from pydantic import BaseModel, Field
from app.models.schemas import EvidenceItem, ConflictItem
from app.services.llm_service import llm_service
from app.agent.prompts import CONFLICT_DETECTOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class ConflictAnalysisResult(BaseModel):
    conflicts: List[ConflictItem] = Field(default_factory=list, description="List of identified disagreements or divergences")

class ConflictDetector:
    def detect_conflicts(self, question: str, evidence: List[EvidenceItem]) -> List[ConflictItem]:
        """Cross-reference evidence items to detect contradictions, conflicting claims, or diverging figures."""
        if len(evidence) < 2:
            logger.info("Fewer than 2 evidence items available; skipping conflict detection.")
            return []

        # Prepare evidence summaries for the arbiter LLM
        evidence_digest = []
        for ev in evidence:
            evidence_digest.append(
                f"[{ev.id}] (Source: {ev.source_title} - {ev.source_url})\n"
                f"Claim: {ev.claim}\n"
                f"Quote: \"{ev.verbatim_quote}\"\n"
                f"Contradiction Flag: {ev.contradiction_potential}\n"
            )
        evidence_text = "\n".join(evidence_digest)

        user_prompt = f"""Analyze the extracted evidence items below for genuine disagreements, contradictory claims, conflicting numbers, or divergent timelines regarding the research topic.

Research Question: {question}

EXTRACTED EVIDENCE POOL:
{evidence_text}

INSTRUCTIONS:
1. Identify any claims that disagree with one another (e.g. differing timelines, conflicting cost estimates, divergent performance metrics).
2. DO NOT pick a winner or silently smooth over differences. Present Claim A vs Claim B clearly.
3. State why they diverge (e.g., prototype testing vs mass production, cell-level vs pack-level, differing baseline years, methodology variances).
4. Assign severity ('minor_nuance', 'moderate_divergence', or 'direct_contradiction').
5. If the evidence pool is completely unanimous and has no contradictions, return an empty list of conflicts.
"""
        logger.info("Executing LLM cross-source conflict detection...")
        result = llm_service.generate_structured(
            system_prompt=CONFLICT_DETECTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ConflictAnalysisResult,
            temperature=0.1
        )
        return result.conflicts

conflict_detector = ConflictDetector()
