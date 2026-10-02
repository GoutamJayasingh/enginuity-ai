from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class MeetingRisk(Base):
    __tablename__ = "meeting_risks"

    id = Column(Integer, primary_key=True, index=True)

    risk = Column(Text, nullable=False)

    severity = Column(String, nullable=True)

    status = Column(String, nullable=False, default="open")

    created_at = Column(DateTime, default=datetime.utcnow)

    meeting_note_id = Column(
        Integer,
        ForeignKey("meeting_notes.id"),
        nullable=False
    )

    meeting_note = relationship(
        "MeetingNote",
        back_populates="risks"
    )