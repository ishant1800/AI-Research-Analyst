import asyncio
import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import ResearchSessionRecord
from app.models.schemas import (
    StartResearchRequest,
    VerifyClaimRequest,
    ResearchSessionState,
    ClaimVerification,
    AgentState
)
from app.agent.orchestrator import orchestrator
from app.agent.verifier import verifier
from app.config import settings
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["research"])

# In-memory event queues for live streaming sessions: session_id -> List[asyncio.Queue]
ACTIVE_STREAM_SUBSCRIBERS: Dict[str, List[asyncio.Queue]] = {}
ACTIVE_SESSIONS_CACHE: Dict[str, ResearchSessionState] = {}

def get_session_from_db(session_id: str, db: Session) -> Optional[ResearchSessionRecord]:
    return db.query(ResearchSessionRecord).filter(ResearchSessionRecord.id == session_id).first()

from app.models.schemas import (
    StartResearchRequest,
    VerifyClaimRequest,
    ResearchSessionState,
    ClaimVerification,
    AgentState,
    ResearchPlan,
    SearchResult,
    EvidenceItem,
    ConflictItem,
    VerificationResult,
    FinalResearchReport,
    TimelineEvent
)

def record_to_state(record: ResearchSessionRecord) -> ResearchSessionState:
    state = ResearchSessionState(
        session_id=record.id,
        question=record.question,
        status=AgentState(record.status),
        progress_percentage=record.progress_percentage,
        error=record.error,
        created_at=record.created_at,
        updated_at=record.updated_at
    )
    if record.plan_json:
        state.plan = ResearchPlan.model_validate_json(record.plan_json)
    if record.sources_json:
        data = json.loads(record.sources_json)
        state.sources = [SearchResult.model_validate(x) for x in data]
    if record.evidence_json:
        data = json.loads(record.evidence_json)
        state.evidence = [EvidenceItem.model_validate(x) for x in data]
    if record.conflicts_json:
        data = json.loads(record.conflicts_json)
        state.conflicts = [ConflictItem.model_validate(x) for x in data]
    if record.verification_json:
        state.verification = VerificationResult.model_validate_json(record.verification_json)
    if record.report_json:
        state.report = FinalResearchReport.model_validate_json(record.report_json)
    if record.timeline_json:
        data = json.loads(record.timeline_json)
        state.timeline = [TimelineEvent.model_validate(x) for x in data]
    return state

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "openai_configured": llm_service.has_api_key(),
        "model": settings.OPENAI_MODEL,
        "search_provider": settings.SEARCH_PROVIDER,
        "max_research_loops": settings.MAX_RESEARCH_LOOPS
    }

@router.post("/research/start")
def start_research(request: StartResearchRequest, background_tasks: BackgroundTasks):
    session_id = f"res-{uuid.uuid4().hex[:10]}"

    def event_listener(session_state: ResearchSessionState, event):
        ACTIVE_SESSIONS_CACHE[session_id] = session_state
        if session_id in ACTIVE_STREAM_SUBSCRIBERS:
            payload = {
                "session_id": session_id,
                "event": event.model_dump(mode="json"),
                "status": session_state.status.value,
                "progress": session_state.progress_percentage,
                "plan": session_state.plan.model_dump(mode="json") if session_state.plan else None,
                "sources_count": len(session_state.sources),
                "evidence_count": len(session_state.evidence),
                "conflicts_count": len(session_state.conflicts),
                "has_verification": session_state.verification is not None,
                "has_report": session_state.report is not None,
            }
            if session_state.report:
                payload["report"] = session_state.report.model_dump(mode="json")
            if session_state.verification:
                payload["verification"] = session_state.verification.model_dump(mode="json")
            if session_state.sources:
                payload["sources"] = [s.model_dump(mode="json") for s in session_state.sources]
            if session_state.evidence:
                payload["evidence"] = [e.model_dump(mode="json") for e in session_state.evidence]
            if session_state.conflicts:
                payload["conflicts"] = [c.model_dump(mode="json") for c in session_state.conflicts]

            for q in ACTIVE_STREAM_SUBSCRIBERS[session_id]:
                try:
                    q.put_nowait(payload)
                except Exception as ex:
                    logger.debug(f"Queue push error: {ex}")

    def run_worker():
        orchestrator.run_research(
            session_id=session_id,
            question=request.question,
            deep_mode=request.deep_mode,
            on_event=event_listener
        )

    background_tasks.add_task(run_worker)

    return {
        "session_id": session_id,
        "question": request.question,
        "status": "planning",
        "stream_url": f"/api/research/stream/{session_id}"
    }

@router.get("/research/stream/{session_id}")
async def stream_research(session_id: str):
    """Server-Sent Events (SSE) stream for real-time agent updates."""
    queue = asyncio.Queue()
    if session_id not in ACTIVE_STREAM_SUBSCRIBERS:
        ACTIVE_STREAM_SUBSCRIBERS[session_id] = []
    ACTIVE_STREAM_SUBSCRIBERS[session_id].append(queue)

    async def event_generator():
        try:
            # If there is cached state, immediately send initial dump
            if session_id in ACTIVE_SESSIONS_CACHE:
                cached = ACTIVE_SESSIONS_CACHE[session_id]
                init_payload = {
                    "session_id": session_id,
                    "status": cached.status.value,
                    "progress": cached.progress_percentage,
                    "plan": cached.plan.model_dump(mode="json") if cached.plan else None,
                    "sources": [s.model_dump(mode="json") for s in cached.sources],
                    "evidence": [e.model_dump(mode="json") for e in cached.evidence],
                    "conflicts": [c.model_dump(mode="json") for c in cached.conflicts],
                    "verification": cached.verification.model_dump(mode="json") if cached.verification else None,
                    "report": cached.report.model_dump(mode="json") if cached.report else None,
                    "timeline": [t.model_dump(mode="json") for t in cached.timeline],
                }
                yield f"data: {json.dumps(init_payload)}\n\n"

            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") in ["completed", "failed"]:
                    break
        except asyncio.CancelledError:
            pass
        finally:
            if session_id in ACTIVE_STREAM_SUBSCRIBERS and queue in ACTIVE_STREAM_SUBSCRIBERS[session_id]:
                ACTIVE_STREAM_SUBSCRIBERS[session_id].remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/research/sessions")
def list_sessions(db: Session = Depends(get_db)):
    """Fetch history of all research sessions."""
    records = db.query(ResearchSessionRecord).order_by(ResearchSessionRecord.created_at.desc()).limit(30).all()
    sessions = []
    for r in records:
        sessions.append({
            "session_id": r.id,
            "question": r.question,
            "status": r.status,
            "progress_percentage": r.progress_percentage,
            "has_report": bool(r.report_json),
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None
        })
    return sessions

@router.get("/research/sessions/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Retrieve full details of a specific research session."""
    record = get_session_from_db(session_id, db)
    if not record:
        raise HTTPException(status_code=404, detail="Research session not found")
    return record_to_state(record)

@router.delete("/research/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a research session."""
    record = get_session_from_db(session_id, db)
    if not record:
        raise HTTPException(status_code=404, detail="Research session not found")
    db.delete(record)
    db.commit()
    if session_id in ACTIVE_SESSIONS_CACHE:
        del ACTIVE_SESSIONS_CACHE[session_id]
    return {"deleted": True, "session_id": session_id}

@router.post("/research/verify-claim", response_model=ClaimVerification)
def verify_claim(req: VerifyClaimRequest, db: Session = Depends(get_db)):
    """Interactive endpoint to audit a custom claim against a session's evidence pool."""
    record = get_session_from_db(req.session_id, db)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = record_to_state(record)
    from app.models.schemas import EvidenceItem
    evidence_items = [EvidenceItem.model_validate(e) if isinstance(e, dict) else e for e in state.evidence]
    
    result = verifier.verify_single_claim(req.claim_text, evidence_items)
    return result
