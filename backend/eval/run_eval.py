import sys
import logging
from typing import Dict, Any, List
from app.agent.orchestrator import orchestrator
from app.models.schemas import ResearchSessionState
from eval.dataset import EVALUATION_DATASET

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("eval_runner")

def evaluate_session(benchmark: Dict[str, Any], session: ResearchSessionState) -> Dict[str, Any]:
    expected = benchmark["expected_properties"]
    report = session.report
    scores = {}
    notes = []

    # 1. Plan Sub-Questions Check
    sub_q_count = len(session.plan.sub_questions) if session.plan else 0
    scores["plan_decomposition"] = 1.0 if sub_q_count >= expected["min_sub_questions"] else (sub_q_count / expected["min_sub_questions"])
    if sub_q_count < expected["min_sub_questions"]:
        notes.append(f"Sub-questions count {sub_q_count} below target {expected['min_sub_questions']}")

    # 2. Source Count Check
    source_count = len(session.sources)
    scores["retrieval_volume"] = min(1.0, source_count / 3.0)

    # 3. Evidence Extraction & Provenance
    evidence_count = len(session.evidence)
    quotes_valid = sum(1 for e in session.evidence if e.verbatim_quote and len(e.verbatim_quote) > 10)
    scores["evidence_provenance"] = quotes_valid / evidence_count if evidence_count > 0 else 0.0

    # 4. Conflict Detection
    if expected["requires_conflict_detection"]:
        scores["conflict_detection"] = 1.0 if len(session.conflicts) > 0 else 0.5
    else:
        scores["conflict_detection"] = 1.0

    # 5. Verification Score
    grounding = session.verification.overall_grounding_score if session.verification else 0.0
    scores["grounding_score"] = grounding

    # 6. Report & Citation Integrity
    if report:
        has_table = len(report.comparison_tables) > 0 if expected["requires_comparison_table"] else True
        ref_count = len(report.references)
        ref_score = min(1.0, ref_count / expected["min_cited_references"])
        
        # Check inline citation references e.g. [1]
        inline_citations_found = any("[" in kf.detailed_explanation for kf in report.key_findings)
        citation_integrity = 1.0 if (inline_citations_found and ref_score >= 1.0) else 0.7
        
        scores["report_synthesis"] = 1.0 if has_table else 0.8
        scores["citation_integrity"] = citation_integrity
    else:
        scores["report_synthesis"] = 0.0
        scores["citation_integrity"] = 0.0
        notes.append("Final report was missing or null")

    total_score = sum(scores.values()) / len(scores)
    
    return {
        "benchmark_id": benchmark["id"],
        "question": benchmark["question"],
        "status": session.status.value,
        "total_score": round(total_score, 3),
        "metrics": scores,
        "notes": notes,
        "passed": total_score >= 0.80
    }

def run_all_evaluations() -> List[Dict[str, Any]]:
    print("=" * 80)
    print("RUNNING AGENTIC AI RESEARCH ANALYST BENCHMARK EVALUATIONS")
    print("=" * 80)
    
    results = []
    for benchmark in EVALUATION_DATASET:
        print(f"\n[Evaluating Benchmark: {benchmark['id']}] {benchmark['question']}")
        session_id = f"eval-{benchmark['id']}"
        session = orchestrator.run_research(session_id=session_id, question=benchmark["question"])
        eval_result = evaluate_session(benchmark, session)
        results.append(eval_result)
        
        print(f"Status: {eval_result['status']}")
        print(f"Composite Score: {eval_result['total_score']} / 1.00 (Passed: {eval_result['passed']})")
        for k, v in eval_result["metrics"].items():
            print(f"  - {k}: {round(v, 2)}")
        if eval_result["notes"]:
            print(f"  Notes: {', '.join(eval_result['notes'])}")

    avg_score = sum(r["total_score"] for r in results) / len(results)
    pass_rate = sum(1 for r in results if r["passed"]) / len(results) * 100
    print("\n" + "=" * 80)
    print(f"BENCHMARK SUMMARY: Overall Average Score: {round(avg_score, 3)} | Pass Rate: {round(pass_rate, 1)}%")
    print("=" * 80)
    return results

if __name__ == "__main__":
    results = run_all_evaluations()
    all_passed = all(r["passed"] for r in results)
    sys.exit(0 if all_passed else 1)
