import logging
from typing import List
from pydantic import BaseModel, Field
from app.models.schemas import ResearchPlan, SearchResult, EvidenceItem
from app.services.llm_service import llm_service
from app.agent.prompts import EVIDENCE_EXTRACTOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class EvidenceExtractionResult(BaseModel):
    evidence_items: List[EvidenceItem] = Field(description="Discrete extracted evidence items with direct quotes")

class EvidenceExtractor:
    def extract(self, plan: ResearchPlan, sources: List[SearchResult]) -> List[EvidenceItem]:
        """Extract atomic evidence items with strict source attribution and verbatim quotes."""
        if not sources:
            logger.warning("No sources available for evidence extraction.")
            return []

        # Prepare formatted sources payload
        sources_text_blocks = []
        for i, s in enumerate(sources[:8], 1):
            text_body = s.content or s.snippet
            snippet_cleaned = text_body[:1800].replace("\n", " ")
            sources_text_blocks.append(
                f"SOURCE [{i}]\nTitle: {s.title}\nURL: {s.url}\nText:\n{snippet_cleaned}\n"
            )

        sources_payload = "\n----------------------------------------\n".join(sources_text_blocks)

        user_prompt = f"""Extract concrete, atomic evidence items from the retrieved sources below to answer the research sub-questions.

Main Research Question: {plan.main_question}

Sub-Questions to address:
{chr(10).join([f"- [{sq.id}] {sq.question} (Purpose: {sq.purpose})" for sq in plan.sub_questions])}

RETRIEVED SOURCES:
{sources_payload}

REQUIREMENTS:
1. For every finding, provide:
   - Specific sub_question_id
   - Clear atomic claim
   - Exact verbatim quote copied directly from the source text above (Anti-Hallucination requirement!)
   - Source title and URL
   - Realistic confidence score (0.0 to 1.0)
   - Contradiction flag if it disputes other sources
2. Extract 4 to 8 high-value evidence items.
"""
        logger.info("Calling LLM for structured evidence extraction...")
        result = llm_service.generate_structured(
            system_prompt=EVIDENCE_EXTRACTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=EvidenceExtractionResult,
            temperature=0.1
        )
        return result.evidence_items

evidence_extractor = EvidenceExtractor()
