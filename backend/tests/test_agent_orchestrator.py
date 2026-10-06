import pytest
from app.agent.orchestrator import orchestrator
from app.models.schemas import AgentState

def test_orchestrator_full_workflow():
    session_id = "test-session-orch-01"
    question = "Will solid-state batteries replace lithium-ion before 2030?"
    
    events_collected = []
    def on_event(sess, event):
        events_collected.append((event.stage, event.message))

    session = orchestrator.run_research(
        session_id=session_id,
        question=question,
        deep_mode=False,
        on_event=on_event
    )

    assert session.session_id == session_id
    assert session.status == AgentState.COMPLETED
    assert session.progress_percentage == 100
    assert session.plan is not None
    assert len(session.sources) > 0
    assert len(session.evidence) > 0
    assert session.verification is not None
    assert session.report is not None
    assert len(events_collected) >= 5
