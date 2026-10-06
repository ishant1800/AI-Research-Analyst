import logging
from app.models.schemas import ResearchPlan
from app.services.llm_service import llm_service
from app.agent.prompts import PLANNER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class ResearchPlanner:
    def plan(self, question: str) -> ResearchPlan:
        """Decompose a complex research question into a structured plan."""
        logger.info(f"Generating research plan for: {question}")
        user_prompt = f"""Generate a rigorous, multi-faceted research plan for the following research question:

Question: {question}

Ensure you provide:
1. Clarified scope and key inquiry dimensions
2. Key empirical and factual information required
3. 3 to 4 granular sub-questions with corresponding targeted search queries
4. Overall search strategy and estimated iterations (3 to 4)
"""
        plan = llm_service.generate_structured(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ResearchPlan,
            temperature=0.2
        )
        return plan

planner = ResearchPlanner()
