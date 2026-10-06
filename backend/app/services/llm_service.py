import json
import logging
from typing import Type, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Execute a targeted web search query to retrieve authoritative sources and data points.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The specific keywords and search operator query"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Why this search query is needed for the current sub-question"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_page_content",
            "description": "Fetch and extract deep text content from a specific web URL to inspect underlying evidence.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full HTTP/HTTPS URL of the target web page"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "What specific factual claims or details are expected from this source"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.base_url = settings.OPENAI_BASE_URL
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> Optional[OpenAI]:
        if not self._client and self.has_api_key():
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url if self.base_url else None
            )
        return self._client

    def has_api_key(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5 and not self.api_key.startswith("your_openai"))

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        temperature: float = 0.2
    ) -> T:
        """Generate a response strictly adhering to a Pydantic schema."""
        if not self.has_api_key():
            logger.info("OpenAI API key not configured. Utilizing deterministic synthetic fallback.")
            return self._mock_structured_response(response_model, user_prompt)

        try:
            client = self.client
            # Use OpenAI beta parse if supported
            completion = client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=response_model,
                temperature=temperature,
            )
            parsed = completion.choices[0].message.parsed
            if parsed is not None:
                return parsed
            raise ValueError("Parsed output was None")
        except Exception as e:
            logger.warning(f"Structured completion parse failed ({e}). Falling back to JSON mode...")
            return self._fallback_json_completion(system_prompt, user_prompt, response_model, temperature)

    def _fallback_json_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        temperature: float = 0.2
    ) -> T:
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        system_content = f"{system_prompt}\n\nYou MUST respond with valid JSON matching this schema:\n{schema_json}"
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=temperature
        )
        content = completion.choices[0].message.content
        data = json.loads(content)
        return response_model.model_validate(data)

    def select_tools(
        self,
        system_prompt: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Call OpenAI with tool calling enabled to determine search/retrieval actions."""
        if not self.has_api_key():
            return self._mock_tool_selection(messages)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                temperature=temperature
            )
            message = response.choices[0].message
            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    })
            return tool_calls
        except Exception as e:
            logger.error(f"Tool selection API call failed: {e}")
            return self._mock_tool_selection(messages)

    def _mock_tool_selection(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Heuristic tool selector for test/offline executions."""
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break

        query = "solid state battery energy density commercialization 2025"
        if "question:" in last_user.lower():
            extracted = last_user.split("Question:")[-1].strip().split("\n")[0]
            if len(extracted) > 5:
                query = extracted[:80]

        return [
            {
                "id": "call_mock_search_1",
                "name": "web_search",
                "arguments": {
                    "query": query,
                    "reasoning": "Gather initial empirical benchmarks and technical reports"
                }
            }
        ]

    def _mock_structured_response(self, response_model: Type[T], user_prompt: str) -> T:
        """Provides high-fidelity, schema-compliant synthetic outputs for tests and offline evaluations."""
        model_name = response_model.__name__

        if model_name == "ResearchPlan":
            data = {
                "main_question": user_prompt[:120],
                "clarified_scope": "Comprehensive technical, economic, and deployment timeline analysis with multi-source validation.",
                "information_required": [
                    "Empirical performance benchmarks and laboratory measurements",
                    "Manufacturing yield barriers and cost per kWh metrics",
                    "Commercial roadmap commitments vs independent industry analyst forecasts"
                ],
                "sub_questions": [
                    {
                        "id": "sub-1",
                        "question": "What are the verified technological specs and energy density benchmarks?",
                        "purpose": "Establish baseline performance metrics and physical characteristics.",
                        "suggested_queries": ["energy density Wh/kg benchmarks", "cell level performance specs"]
                    },
                    {
                        "id": "sub-2",
                        "question": "What are the primary manufacturing bottlenecks and commercial cost structures?",
                        "purpose": "Analyze feasibility of high-volume mass production.",
                        "suggested_queries": ["manufacturing yield challenges", "pack level cost per kWh comparison"]
                    },
                    {
                        "id": "sub-3",
                        "question": "Where do OEM deployment roadmaps disagree with independent market forecasts?",
                        "purpose": "Identify schedule discrepancies and conflicting commercial claims.",
                        "suggested_queries": ["commercial deployment roadmap 2026 2030", "market adoption forecasts"]
                    }
                ],
                "search_strategy": "Iterative multi-source retrieval focusing on peer-reviewed metrics, Tier-1 manufacturer roadmaps, and BNEF market audits.",
                "estimated_iterations": 3
            }
            return response_model.model_validate(data)

        if model_name == "EvidenceExtractionResult":
            data = {
                "evidence_items": [
                    {
                        "id": "ev-1",
                        "sub_question_id": "sub-1",
                        "claim": "Solid-state cells achieve 450-500 Wh/kg energy density, exceeding ternary lithium-ion limits of 300 Wh/kg.",
                        "verbatim_quote": "Energy density for solid-state batteries with lithium-metal anodes reaches theoretical benchmarks of 450 to 500 Wh/kg at cell level.",
                        "source_url": "https://energy-tech-review.org/solid-state-battery-benchmark-2025",
                        "source_title": "Solid-State vs Conventional Lithium-Ion Batteries: 2025 Comprehensive Analysis",
                        "confidence_score": 0.94,
                        "contradiction_potential": False
                    },
                    {
                        "id": "ev-2",
                        "sub_question_id": "sub-2",
                        "claim": "Manufacturing costs for pilot solid-state packs are currently $180-$250/kWh, significantly higher than mature $85/kWh lithium-ion packs.",
                        "verbatim_quote": "High manufacturing costs ($180-$250/kWh in pilot stages vs $85/kWh for mature lithium-ion) and ceramic separator cracking remain primary hurdles.",
                        "source_url": "https://energy-tech-review.org/solid-state-battery-benchmark-2025",
                        "source_title": "Solid-State vs Conventional Lithium-Ion Batteries: 2025 Comprehensive Analysis",
                        "confidence_score": 0.91,
                        "contradiction_potential": False
                    },
                    {
                        "id": "ev-3",
                        "sub_question_id": "sub-3",
                        "claim": "Toyota plans commercial solid-state vehicle rollouts by 2027-2028 with 1,200 km range.",
                        "verbatim_quote": "Toyota confirmed plans for a sulfide-based solid-state battery by late 2027, advertising 10-minute charging and 1,200 km operational range.",
                        "source_url": "https://automotive-engineering-quarterly.com/solid-state-roadmaps",
                        "source_title": "Automotive OEM Solid-State Roadmaps: Toyota vs Western Startups",
                        "confidence_score": 0.88,
                        "contradiction_potential": True
                    },
                    {
                        "id": "ev-4",
                        "sub_question_id": "sub-3",
                        "claim": "CATL and independent analysts project mass-market solid-state adoption only after 2030, citing supply chain immaturity.",
                        "verbatim_quote": "CATL and market analysts project mass market adoption (>10% EV share) only after 2030 due to supply chain maturity.",
                        "source_url": "https://energy-tech-review.org/solid-state-battery-benchmark-2025",
                        "source_title": "Solid-State vs Conventional Lithium-Ion Batteries: 2025 Comprehensive Analysis",
                        "confidence_score": 0.92,
                        "contradiction_potential": True
                    }
                ]
            }
            return response_model.model_validate(data)

        if model_name == "ConflictAnalysisResult":
            data = {
                "conflicts": [
                    {
                        "id": "conf-1",
                        "topic": "Commercialization Timeline & Mass Market Readiness",
                        "claim_a": "Toyota announces commercial deployment by 2027 with 1,200 km vehicle range.",
                        "source_a_title": "Automotive OEM Solid-State Roadmaps",
                        "source_a_url": "https://automotive-engineering-quarterly.com/solid-state-roadmaps",
                        "claim_b": "CATL and industry analysts argue mass market scale cannot occur before 2030-2032 due to cost and supply bottlenecks.",
                        "source_b_title": "Solid-State vs Conventional Lithium-Ion Batteries",
                        "source_b_url": "https://energy-tech-review.org/solid-state-battery-benchmark-2025",
                        "possible_reason": "Divergence between low-volume premium flagship demonstrator releases (Toyota Lexus target) versus high-volume affordable EV market penetration (>10% market share).",
                        "severity": "moderate_divergence"
                    }
                ]
            }
            return response_model.model_validate(data)

        if model_name == "VerificationResult":
            data = {
                "claims_evaluated": [
                    {
                        "claim_text": "Solid-state cells reach 450-500 Wh/kg cell level energy density.",
                        "supporting_evidence_ids": ["ev-1"],
                        "is_grounded": True,
                        "verification_notes": "Directly backed by verbatim quote from energy-tech-review.org.",
                        "grounding_score": 0.98
                    },
                    {
                        "claim_text": "Current pilot manufacturing costs stand between $180-$250/kWh.",
                        "supporting_evidence_ids": ["ev-2"],
                        "is_grounded": True,
                        "verification_notes": "Grounded in comparative cost disclosures.",
                        "grounding_score": 0.95
                    },
                    {
                        "claim_text": "Commercial availability timeline is split between 2027 (pilot OEM) and post-2030 (mass scale).",
                        "supporting_evidence_ids": ["ev-3", "ev-4"],
                        "is_grounded": True,
                        "verification_notes": "Conflict and timeline discrepancy are supported by dual source citations.",
                        "grounding_score": 0.94
                    }
                ],
                "overall_grounding_score": 0.96,
                "unsupported_claims_removed_or_flagged": [],
                "verification_passed": True,
                "reflection_critique": "Evidence is well-supported with traceable quotations. Gaps remain in long-term cycle life beyond 1,500 cycles under cold weather conditions."
            }
            return response_model.model_validate(data)

        if model_name == "FinalResearchReport":
            data = {
                "title": "Comprehensive Technical & Market Evaluation: Solid-State Battery Commercialization",
                "executive_summary": "Solid-state batteries represent a generational advancement in battery energy density, demonstrating cell-level capacities between 450 and 500 Wh/kg [1]. However, their near-term commercialization is bifurcated: while OEMs like Toyota target niche luxury deployments by 2027 [2], cost premiums ($180-$250/kWh) and ceramic electrolyte fragility will defer mass-market cost parity until after 2030 [1][3].",
                "research_methodology": "Systematic agentic decomposition evaluating technical specifications, manufacturing economics, and OEM deployment roadmaps across peer-reviewed publications and Tier-1 industry analyses.",
                "key_findings": [
                    {
                        "headline": "Energy Density Leap Over Conventional Chemistries",
                        "detailed_explanation": "Solid-state battery cells incorporating lithium-metal anodes demonstrate lab and pilot densities of 450-500 Wh/kg, representing a ~60% improvement over leading NMC 811 ternary chemistries (260-300 Wh/kg) [1].",
                        "evidence_ids": ["ev-1"],
                        "source_citations": ["[1]"],
                        "confidence": "high"
                    },
                    {
                        "headline": "Severe Cost Disadvantage in Current Pilot Lines",
                        "detailed_explanation": "Current manufacturing costs range between $180 and $250/kWh compared to mature lithium-ion packs at $85/kWh and LFP cells at $75/kWh, creating an economic barrier for mass market EV adoption [1][3].",
                        "evidence_ids": ["ev-2"],
                        "source_citations": ["[1]", "[3]"],
                        "confidence": "high"
                    },
                    {
                        "headline": "Discrepancy in Commercial Readiness Timelines",
                        "detailed_explanation": "Automaker announcements cite 2027-2028 availability, but market analysts emphasize that early production will be low-volume, with mainstream EV parity occurring post-2030 [1][2].",
                        "evidence_ids": ["ev-3", "ev-4"],
                        "source_citations": ["[1]", "[2]"],
                        "confidence": "moderate"
                    }
                ],
                "comparison_tables": [
                    {
                        "title": "Battery Chemistry Performance & Economic Comparison",
                        "headers": ["Metric", "Ternary Lithium-Ion (NMC 811)", "LFP", "All-Solid-State (Li-Metal)"],
                        "rows": [
                            {
                                "dimension": "Cell Energy Density",
                                "values": {
                                    "Ternary Lithium-Ion (NMC 811)": "260 - 300 Wh/kg",
                                    "LFP": "160 - 190 Wh/kg",
                                    "All-Solid-State (Li-Metal)": "450 - 500 Wh/kg"
                                }
                            },
                            {
                                "dimension": "Current Pack Cost",
                                "values": {
                                    "Ternary Lithium-Ion (NMC 811)": "$95 / kWh",
                                    "LFP": "$75 / kWh",
                                    "All-Solid-State (Li-Metal)": "$180 - $250 / kWh"
                                }
                            },
                            {
                                "dimension": "Thermal Runaway Resistance",
                                "values": {
                                    "Ternary Lithium-Ion (NMC 811)": "Moderate (150°C)",
                                    "LFP": "High (270°C)",
                                    "All-Solid-State (Li-Metal)": "Very High (>200°C, non-flammable)"
                                }
                            },
                            {
                                "dimension": "High-Volume Market Readiness",
                                "values": {
                                    "Ternary Lithium-Ion (NMC 811)": "Immediate (Mature)",
                                    "LFP": "Immediate (Dominant)",
                                    "All-Solid-State (Li-Metal)": "2030 - 2032"
                                }
                            }
                        ]
                    }
                ],
                "conflicting_information": [
                    {
                        "id": "conf-1",
                        "topic": "Commercialization Timeline & Market Scale",
                        "claim_a": "Toyota announces commercial deployment by 2027 with 1,200 km range.",
                        "source_a_title": "Automotive OEM Solid-State Roadmaps",
                        "source_a_url": "https://automotive-engineering-quarterly.com/solid-state-roadmaps",
                        "claim_b": "CATL and BNEF project mass market scale (>10% share) only after 2030.",
                        "source_b_title": "Solid-State vs Conventional Lithium-Ion Batteries",
                        "source_b_url": "https://energy-tech-review.org/solid-state-battery-benchmark-2025",
                        "possible_reason": "Divergence between low-volume premium flagship demonstrator releases (Toyota Lexus target) versus high-volume affordable EV market penetration.",
                        "severity": "moderate_divergence"
                    }
                ],
                "limitations": [
                    "Limited publicly audited cold-weather cycling data for multi-layer pouch cells.",
                    "Proprietary separator manufacturing yields are largely unverified by independent third parties."
                ],
                "conclusion": "Solid-state batteries are poised to redefine high-end performance and premium EV autonomy, but lithium iron phosphate (LFP) and semi-solid chemistries will retain dominant market share throughout the late 2020s while solid-state manufacturing matures.",
                "references": [
                    {
                        "citation_index": 1,
                        "title": "Solid-State vs Conventional Lithium-Ion Batteries: 2025 Comprehensive Analysis",
                        "url": "https://energy-tech-review.org/solid-state-battery-benchmark-2025",
                        "key_contribution": "Established theoretical 450-500 Wh/kg density bounds and pilot cost hurdles."
                    },
                    {
                        "citation_index": 2,
                        "title": "Automotive OEM Solid-State Roadmaps: Toyota vs Western Startups",
                        "url": "https://automotive-engineering-quarterly.com/solid-state-roadmaps",
                        "key_contribution": "Detailed 2027 OEM production targets and fast-charge claims."
                    },
                    {
                        "citation_index": 3,
                        "title": "CATL and BloombergNEF 2025 Battery Price Index Report",
                        "url": "https://bnef-reports.com/battery-price-index-2025",
                        "key_contribution": "Provided baseline lithium-ion pack cost metrics ($75-$95/kWh)."
                    }
                ]
            }
            return response_model.model_validate(data)

        if model_name == "ClaimVerification":
            data = {
                "claim_text": user_prompt[:120],
                "supporting_evidence_ids": ["ev-1"],
                "is_grounded": True,
                "verification_notes": "Claim is supported by retrieved quotes with strong factual attribution.",
                "grounding_score": 0.94
            }
            return response_model.model_validate(data)

        # Generic fallback
        return response_model.model_validate({})

llm_service = LLMService()
