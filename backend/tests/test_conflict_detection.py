import pytest
from app.models.schemas import EvidenceItem
from app.agent.conflict_detector import conflict_detector

def test_conflict_detection_identifies_opposing_claims():
    evidence = [
        EvidenceItem(
            id="ev-1",
            sub_question_id="sub-1",
            claim="Toyota plans commercial solid-state rollout by 2027.",
            verbatim_quote="Toyota confirmed plans for a sulfide-based solid-state battery by late 2027.",
            source_url="https://automotive-engineering-quarterly.com/solid-state-roadmaps",
            source_title="Automotive OEM Solid-State Roadmaps",
            confidence_score=0.90,
            contradiction_potential=True
        ),
        EvidenceItem(
            id="ev-2",
            sub_question_id="sub-1",
            claim="CATL and market analysts project mass market adoption only after 2030 due to supply chain immaturity.",
            verbatim_quote="CATL and market analysts project mass market adoption (>10% EV share) only after 2030 due to supply chain maturity.",
            source_url="https://energy-tech-review.org/solid-state-battery-benchmark-2025",
            source_title="Solid-State vs Conventional Lithium-Ion Batteries",
            confidence_score=0.92,
            contradiction_potential=True
        )
    ]

    conflicts = conflict_detector.detect_conflicts(
        question="When will solid-state batteries be commercially deployed?",
        evidence=evidence
    )

    assert len(conflicts) > 0
    first_conflict = conflicts[0]
    assert first_conflict.topic is not None
    assert first_conflict.claim_a is not None
    assert first_conflict.claim_b is not None
    assert len(first_conflict.possible_reason) > 5
    assert first_conflict.severity in ["minor_nuance", "moderate_divergence", "direct_contradiction"]

def test_conflict_detection_single_item_returns_empty():
    evidence = [
        EvidenceItem(
            id="ev-1",
            sub_question_id="sub-1",
            claim="Single claim",
            verbatim_quote="quote",
            source_url="https://example.com",
            source_title="Source",
            confidence_score=0.9,
            contradiction_potential=False
        )
    ]
    conflicts = conflict_detector.detect_conflicts(question="Question?", evidence=evidence)
    assert conflicts == []
