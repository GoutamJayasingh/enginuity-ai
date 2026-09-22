from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class MeetingActionItem(Base):
    __tablename__ = "meeting_action_items"

    id = Column(Integer, primary_key=True, index=True)

    action_item = Column(Text, nullable=False)

    assignee = Column(String, nullable=True)

    due_date = Column(DateTime, nullable=True)

    status = Column(String, nullable=False, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)

    meeting_note_id = Column(
        Integer,
        ForeignKey("meeting_notes.id"),
        nullable=False
    )

    meeting_note = relationship(
        "MeetingNote",
        back_populates="action_items"
    )