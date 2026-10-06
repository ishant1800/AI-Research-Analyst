import logging
import uuid
import json
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

from app.models.schemas import (
    AgentState,
    ResearchPlan,
    SearchResult,
    EvidenceItem,
    ConflictItem,
    VerificationResult,
    FinalResearchReport,
    TimelineEvent,
    ResearchSessionState,
    ToolCallLog
)
from app.agent.planner import planner
from app.agent.researcher import ToolResearcher
from app.agent.evidence_extractor import evidence_extractor
from app.agent.conflict_detector import conflict_detector
from app.agent.verifier import verifier
from app.agent.synthesizer import synthesizer
from app.database.db import SessionLocal
from app.database.models import ResearchSessionRecord
from app.config import settings

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        pass

    def run_research(
        self,
        session_id: str,
        question: str,
        deep_mode: bool = False,
        on_event: Optional[Callable[[ResearchSessionState, TimelineEvent], None]] = None
    ) -> ResearchSessionState:
        """Execute the full research state machine synchronously or in a worker thread."""
        logger.info(f"Starting research session {session_id} for question: {question}")
        
        session = ResearchSessionState(
            session_id=session_id,
            question=question,
            status=AgentState.PLANNING,
            progress_percentage=5,
            timeline=[]
        )

        def emit(stage: AgentState, progress: int, message: str, data: Optional[Dict[str, Any]] = None):
            session.status = stage
            session.progress_percentage = progress
            session.updated_at = datetime.utcnow()
            event = TimelineEvent(
                id=f"evt-{uuid.uuid4().hex[:8]}",
                stage=stage,
                message=message,
                timestamp=datetime.utcnow(),
                data=data
            )
            session.timeline.append(event)
            self._save_checkpoint(session)
            if on_event:
                try:
                    on_event(session, event)
                except Exception as ex:
                    logger.warning(f"Event callback error: {ex}")

        # Initial event
        emit(AgentState.PLANNING, 10, f"Decomposing research question into structured inquiry plan...")

        try:
            # 1. PLANNING PHASE
            plan: ResearchPlan = planner.plan(question)
            session.plan = plan
            emit(
                AgentState.PLANNING,
                25,
                f"Generated research plan with {len(plan.sub_questions)} focused sub-questions.",
                {"sub_questions_count": len(plan.sub_questions)}
            )

            # 2. RETRIEVAL & TOOL CALLING PHASE
            max_loops = 5 if deep_mode else settings.MAX_RESEARCH_LOOPS
            researcher_instance = ToolResearcher(max_loops=max_loops)

            emit(AgentState.RETRIEVING, 30, f"Executing bounded search and evidence retrieval loop (Max loops: {max_loops})...")

            def on_tool(log: ToolCallLog):
                emit(
                    AgentState.RETRIEVING,
                    min(55, session.progress_percentage + 4),
                    f"Tool called: {log.tool_name} (Iteration {log.iteration}) -> {log.summary_result}",
                    {"tool_name": log.tool_name, "arguments": log.arguments}
                )

            sources: List[SearchResult] = researcher_instance.execute_retrieval(plan, on_tool_call=on_tool)
            session.sources = sources
            emit(
                AgentState.RETRIEVING,
                55,
                f"Retrieved and indexed {len(sources)} unique authoritative sources.",
                {"total_sources": len(sources)}
            )

            # 3. EVIDENCE EXTRACTION PHASE
            emit(AgentState.EXTRACTING_EVIDENCE, 60, "Extracting atomic factual evidence with verbatim provenance quotes...")
            evidence: List[EvidenceItem] = evidence_extractor.extract(plan, sources)
            session.evidence = evidence
            emit(
                AgentState.EXTRACTING_EVIDENCE,
                70,
                f"Extracted {len(evidence)} atomic evidence items with source quotes.",
                {"evidence_count": len(evidence)}
            )

            # 4. CONFLICT DETECTION PHASE
            emit(AgentState.ANALYZING_CONFLICTS, 75, "Analyzing cross-source evidence for contradictions and diverging metrics...")
            conflicts: List[ConflictItem] = conflict_detector.detect_conflicts(question, evidence)
            session.conflicts = conflicts
            if conflicts:
                emit(
                    AgentState.ANALYZING_CONFLICTS,
                    80,
                    f"Identified {len(conflicts)} disagreements across sources. Preserving competing perspectives.",
                    {"conflicts_count": len(conflicts)}
                )
            else:
                emit(
                    AgentState.ANALYZING_CONFLICTS,
                    80,
                    "Cross-source analysis complete: High consensus observed across retrieved evidence.",
                    {"conflicts_count": 0}
                )

            # 5. VERIFICATION & REFLECTION PHASE
            emit(AgentState.VERIFYING, 85, "Executing pre-synthesis audit: Verifying claim grounding against raw source quotes...")
            verification: VerificationResult = verifier.verify(question, evidence, conflicts)
            session.verification = verification
            emit(
                AgentState.VERIFYING,
                90,
                f"Audit completed: Overall grounding score {int(verification.overall_grounding_score * 100)}%. "
                f"Verified: {verification.verification_passed}.",
                {"grounding_score": verification.overall_grounding_score}
            )

            # 6. SYNTHESIS PHASE
            emit(AgentState.SYNTHESIZING, 95, "Compiling publication-grade research report with structured citations and comparison tables...")
            report: FinalResearchReport = synthesizer.synthesize(
                plan=plan,
                sources=sources,
                evidence=evidence,
                conflicts=conflicts,
                verification=verification
            )
            session.report = report

            # 7. COMPLETION
            emit(
                AgentState.COMPLETED,
                100,
                f"Research report generation complete: '{report.title}' with {len(report.references)} cited sources.",
                {"report_title": report.title}
            )

        except Exception as e:
            logger.exception(f"Research run failed for session {session_id}: {e}")
            session.error = str(e)
            emit(AgentState.FAILED, session.progress_percentage, f"Research error encountered: {str(e)}")

        return session

    def _save_checkpoint(self, session: ResearchSessionState):
        """Persist state to SQLite database."""
        try:
            db = SessionLocal()
            try:
                record = db.query(ResearchSessionRecord).filter(ResearchSessionRecord.id == session.session_id).first()
                if not record:
                    record = ResearchSessionRecord(
                        id=session.session_id,
                        question=session.question,
                        created_at=session.created_at
                    )
                    db.add(record)

                record.status = session.status.value
                record.progress_percentage = session.progress_percentage
                record.updated_at = datetime.utcnow()
                record.error = session.error

                if session.plan:
                    record.plan_json = session.plan.model_dump_json()
                if session.sources:
                    record.sources_json = json.dumps([s.model_dump(mode="json") for s in session.sources])
                if session.evidence:
                    record.evidence_json = json.dumps([e.model_dump(mode="json") for e in session.evidence])
                if session.conflicts:
                    record.conflicts_json = json.dumps([c.model_dump(mode="json") for c in session.conflicts])
                if session.verification:
                    record.verification_json = session.verification.model_dump_json()
                if session.report:
                    record.report_json = session.report.model_dump_json()
                if session.timeline:
                    record.timeline_json = json.dumps([t.model_dump(mode="json") for t in session.timeline])

                db.commit()
            finally:
                db.close()
        except Exception as ex:
            logger.error(f"Failed to persist research checkpoint: {ex}")

orchestrator = AgentOrchestrator()
