import pytest
from app.models.schemas import EvidenceItem, ConflictItem
from app.agent.verifier import verifier

def test_verifier_evaluates_evidence_pool():
    evidence = [
        EvidenceItem(
            id="ev-1",
            sub_question_id="sub-1",
            claim="Solid-state cells achieve 450-500 Wh/kg.",
            verbatim_quote="Solid-state batteries reach theoretical benchmarks of 450 to 500 Wh/kg at cell level.",
            source_url="https://energy-tech-review.org/solid-state",
            source_title="Energy Tech Review",
            confidence_score=0.95,
            contradiction_potential=False
        )
    ]
    conflicts = []

    res = verifier.verify("What is the energy density?", evidence, conflicts)
    assert res.overall_grounding_score >= 0.0 and res.overall_grounding_score <= 1.0
    assert len(res.claims_evaluated) > 0
    assert res.verification_passed is True
    assert len(res.reflection_critique) > 5

def test_verifier_empty_evidence():
    res = verifier.verify("Empty question", [], [])
    assert res.verification_passed is False
    assert res.overall_grounding_score == 0.0

def test_verifier_single_claim_audit():
    evidence = [
        EvidenceItem(
            id="ev-1",
            sub_question_id="sub-1",
            claim="LFP pack costs fell below $80/kWh.",
            verbatim_quote="pack-level costs for LFP batteries fell below $80/kWh",
            source_url="https://bnef-reports.com/battery-price-index-2025",
            source_title="BNEF Report",
            confidence_score=0.95,
            contradiction_potential=False
        )
    ]
    audit = verifier.verify_single_claim("LFP pack prices are under $80/kWh in 2025", evidence)
    assert audit.grounding_score >= 0.0
    assert audit.is_grounded is True
