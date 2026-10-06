from sqlalchemy import Column, String, Integer, Text, DateTime
from datetime import datetime
from app.database.db import Base

class ResearchSessionRecord(Base):
    __tablename__ = "research_sessions"

    id = Column(String(64), primary_key=True, index=True)
    question = Column(Text, nullable=False)
    status = Column(String(32), default="idle", index=True)
    progress_percentage = Column(Integer, default=0)
    
    plan_json = Column(Text, nullable=True)
    sources_json = Column(Text, nullable=True)
    evidence_json = Column(Text, nullable=True)
    conflicts_json = Column(Text, nullable=True)
    verification_json = Column(Text, nullable=True)
    report_json = Column(Text, nullable=True)
    timeline_json = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
