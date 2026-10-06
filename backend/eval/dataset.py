from typing import List, Dict, Any

EVALUATION_DATASET: List[Dict[str, Any]] = [
    {
        "id": "eval-01",
        "question": "Will solid-state batteries replace lithium-ion in commercial EVs before 2030, and what are the main technical hurdles?",
        "topic": "Clean Tech & Energy Storage",
        "expected_properties": {
            "min_sub_questions": 3,
            "must_contain_dimensions": ["energy density", "cost", "manufacturing", "timeline"],
            "requires_conflict_detection": True,
            "expected_conflict_topics": ["timeline", "mass market vs luxury rollout", "cost parity"],
            "requires_comparison_table": True,
            "min_cited_references": 2,
            "min_grounding_score": 0.85
        }
    },
    {
        "id": "eval-02",
        "question": "Are deterministic state-machine agent architectures more reliable in enterprise production than open-ended multi-agent swarms?",
        "topic": "AI Engineering & Systems",
        "expected_properties": {
            "min_sub_questions": 3,
            "must_contain_dimensions": ["latency", "hallucination rates", "debugging", "token costs"],
            "requires_conflict_detection": False,
            "requires_comparison_table": True,
            "min_cited_references": 1,
            "min_grounding_score": 0.85
        }
    },
    {
        "id": "eval-03",
        "question": "How do small language models (SLMs, 7B-14B) compare against frontier LLMs for specialized extraction and verification tasks?",
        "topic": "Machine Learning Benchmarks",
        "expected_properties": {
            "min_sub_questions": 3,
            "must_contain_dimensions": ["accuracy", "cost", "latency", "complex reasoning"],
            "requires_conflict_detection": True,
            "requires_comparison_table": True,
            "min_cited_references": 1,
            "min_grounding_score": 0.85
        }
    }
]
