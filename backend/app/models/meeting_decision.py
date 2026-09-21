from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class MeetingDecision(Base):
    __tablename__ = "meeting_decisions"

    id = Column(Integer, primary_key=True, index=True)

    decision = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    meeting_note_id = Column(
        Integer,
        ForeignKey("meeting_notes.id"),
        nullable=False
    )

    meeting_note = relationship(
        "MeetingNote",
        back_populates="decisions"
    )