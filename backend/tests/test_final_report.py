import pytest
from app.models.schemas import (
    ResearchPlan,
    SubQuestion,
    SearchResult,
    EvidenceItem,
    ConflictItem,
    VerificationResult,
    ClaimVerification
)
from app.agent.synthesizer import synthesizer

def test_report_synthesizer_generates_valid_report():
    plan = ResearchPlan(
        main_question="What is the commercial timeline for solid-state batteries?",
        clarified_scope="Analysis of solid-state EV commercialization.",
        information_required=["Cell energy density", "Manufacturing costs"],
        sub_questions=[
            SubQuestion(
                id="sub-1",
                question="What are verified energy densities?",
                purpose="Baseline specs",
                suggested_queries=["solid state energy density Wh/kg"]
            )
        ],
        search_strategy="Technical retrieval",
        estimated_iterations=3
    )
    sources = [
        SearchResult(
            id="src-1",
            title="Solid-State Battery Review",
            url="https://energy-tech-review.org/solid-state",
            snippet="Solid-state cells achieve 450 Wh/kg at cell level.",
            content="Solid-state cells achieve 450 Wh/kg at cell level.",
            query="solid state density"
        )
    ]
    evidence = [
        EvidenceItem(
            id="ev-1",
            sub_question_id="sub-1",
            claim="Solid-state cells achieve 450-500 Wh/kg.",
            verbatim_quote="Solid-state cells achieve 450 Wh/kg at cell level.",
            source_url="https://energy-tech-review.org/solid-state",
            source_title="Solid-State Battery Review",
            confidence_score=0.94,
            contradiction_potential=False
        )
    ]
    conflicts = []
    verification = VerificationResult(
        claims_evaluated=[
            ClaimVerification(
                claim_text="Solid-state cells achieve 450-500 Wh/kg.",
                supporting_evidence_ids=["ev-1"],
                is_grounded=True,
                verification_notes="Verified via direct quote",
                grounding_score=0.98
            )
        ],
        overall_grounding_score=0.98,
        unsupported_claims_removed_or_flagged=[],
        verification_passed=True,
        reflection_critique="Evidence is grounded."
    )

    report = synthesizer.synthesize(
        plan=plan,
        sources=sources,
        evidence=evidence,
        conflicts=conflicts,
        verification=verification
    )

    assert report.title is not None
    assert len(report.executive_summary) > 20
    assert len(report.key_findings) > 0
    assert len(report.references) > 0
    assert report.references[0].citation_index >= 1
    assert len(report.limitations) > 0
    assert len(report.conclusion) > 10
