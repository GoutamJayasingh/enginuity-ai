from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(String)

    issue_type = Column(String)

    priority = Column(String)

    status = Column(String, default="open")

    created_at = Column(DateTime, default=datetime.utcnow)

    sprint_id = Column(
        Integer,
        ForeignKey("sprints.id")
    )

    sprint = relationship(
        "Sprint",
        back_populates="issues"
    )