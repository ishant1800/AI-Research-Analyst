import pytest
from app.models.schemas import ResearchPlan, SubQuestion, SearchResult
from app.agent.evidence_extractor import evidence_extractor

def test_evidence_extraction_logic():
    plan = ResearchPlan(
        main_question="What is the commercial timeline for solid-state batteries?",
        clarified_scope="Status of solid-state EV commercialization.",
        information_required=["Energy density figures", "Costs"],
        sub_questions=[
            SubQuestion(
                id="sub-1",
                question="What are verified energy densities?",
                purpose="Establish baseline specs",
                suggested_queries=["solid state energy density Wh/kg"]
            )
        ],
        search_strategy="Technical literature",
        estimated_iterations=3
    )
    sources = [
        SearchResult(
            id="src-1",
            title="Solid-State Battery Review",
            url="https://energy-tech-review.org/solid-state",
            snippet="Solid-state cells achieve 450 Wh/kg at cell level.",
            content="Energy density for solid-state batteries with lithium-metal anodes reaches theoretical benchmarks of 450 to 500 Wh/kg at cell level.",
            query="solid state energy density"
        )
    ]

    evidence_items = evidence_extractor.extract(plan, sources)
    assert len(evidence_items) > 0
    first_ev = evidence_items[0]
    assert first_ev.sub_question_id is not None
    assert len(first_ev.claim) > 5
    assert len(first_ev.verbatim_quote) > 5
    assert first_ev.confidence_score >= 0.0 and first_ev.confidence_score <= 1.0

def test_evidence_extraction_empty_sources():
    plan = ResearchPlan(
        main_question="What is the commercial timeline?",
        clarified_scope="Scope",
        information_required=[],
        sub_questions=[],
        search_strategy="Strategy",
        estimated_iterations=2
    )
    evidence_items = evidence_extractor.extract(plan, [])
    assert evidence_items == []
