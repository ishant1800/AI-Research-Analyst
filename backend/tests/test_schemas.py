import pytest
from pydantic import ValidationError
from datetime import datetime
from app.models.schemas import (
    ResearchPlan,
    SubQuestion,
    SearchResult,
    EvidenceItem,
    ConflictItem,
    ClaimVerification,
    VerificationResult,
    ComparisonTable,
    ComparisonRow,
    KeyFinding,
    ReferenceItem,
    FinalResearchReport
)

def test_research_plan_schema_valid():
    plan = ResearchPlan(
        main_question="What is the commercial timeline for solid-state batteries?",
        clarified_scope="Analysis of automotive solid-state deployments from 2025 to 2030.",
        information_required=["Cell energy density", "Manufacturing costs"],
        sub_questions=[
            SubQuestion(
                id="sub-1",
                question="What are verified energy densities?",
                purpose="Establish baseline specs",
                suggested_queries=["solid state energy density Wh/kg"]
            )
        ],
        search_strategy="Multi-source peer reviewed retrieval",
        estimated_iterations=3
    )
    assert plan.main_question.startswith("What is")
    assert len(plan.sub_questions) == 1
    assert plan.sub_questions[0].id == "sub-1"

def test_evidence_item_schema_validation():
    ev = EvidenceItem(
        id="ev-1",
        sub_question_id="sub-1",
        claim="Solid-state cells achieve 450 Wh/kg",
        verbatim_quote="Solid-state cells achieve 450 Wh/kg at cell level.",
        source_url="https://example.com/battery",
        source_title="Battery Tech Review",
        confidence_score=0.95,
        contradiction_potential=False
    )
    assert ev.confidence_score == 0.95
    assert ev.contradiction_potential is False

    # Test confidence score boundaries
    with pytest.raises(ValidationError):
        EvidenceItem(
            id="ev-2",
            sub_question_id="sub-1",
            claim="Invalid confidence",
            verbatim_quote="quote",
            source_url="https://example.com",
            source_title="Title",
            confidence_score=1.5 # Must be <= 1.0
        )

def test_conflict_item_schema():
    conflict = ConflictItem(
        id="conf-1",
        topic="Deployment Timeline",
        claim_a="Rollout in 2027",
        source_a_title="OEM A",
        source_a_url="https://oem-a.com",
        claim_b="Mass market post-2030",
        source_b_title="Analyst B",
        source_b_url="https://analyst-b.com",
        possible_reason="Prototype demonstrator vs high-volume commercial scale.",
        severity="moderate_divergence"
    )
    assert conflict.severity == "moderate_divergence"
    assert "2027" in conflict.claim_a

def test_verification_result_schema():
    res = VerificationResult(
        claims_evaluated=[
            ClaimVerification(
                claim_text="Cells achieve 450 Wh/kg",
                supporting_evidence_ids=["ev-1"],
                is_grounded=True,
                verification_notes="Direct quote confirms metric.",
                grounding_score=0.98
            )
        ],
        overall_grounding_score=0.98,
        unsupported_claims_removed_or_flagged=[],
        verification_passed=True,
        reflection_critique="Evidence pool is robust."
    )
    assert res.verification_passed is True
    assert res.overall_grounding_score == 0.98

def test_final_report_schema():
    report = FinalResearchReport(
        title="Solid-State Battery Status Report",
        executive_summary="Solid-state batteries reach 450 Wh/kg [1] but face commercial bottlenecks [2].",
        research_methodology="Decomposition and iterative retrieval.",
        key_findings=[
            KeyFinding(
                headline="High Energy Density",
                detailed_explanation="Demonstrated 450 Wh/kg [1].",
                evidence_ids=["ev-1"],
                source_citations=["[1]"],
                confidence="high"
            )
        ],
        comparison_tables=[
            ComparisonTable(
                title="Chemistry Metrics",
                headers=["Metric", "Solid-State", "Li-Ion"],
                rows=[
                    ComparisonRow(
                        dimension="Density",
                        values={"Solid-State": "450 Wh/kg", "Li-Ion": "270 Wh/kg"}
                    )
                ]
            )
        ],
        conflicting_information=[],
        limitations=["Laboratory prototype bias"],
        conclusion="Solid-state adoption will begin in premium tiers.",
        references=[
            ReferenceItem(
                citation_index=1,
                title="Battery Tech Review",
                url="https://example.com/battery",
                key_contribution="Energy density measurement"
            )
        ]
    )
    assert len(report.key_findings) == 1
    assert len(report.comparison_tables) == 1
    assert report.references[0].citation_index == 1
