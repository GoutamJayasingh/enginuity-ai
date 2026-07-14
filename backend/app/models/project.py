from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    description = Column(String)

    status = Column(String, default="active")

    created_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))

    github_sync_enabled = Column(
        Boolean,
        default=False,
        nullable=False
    )

    owner = relationship(
        "User",
        back_populates="projects"
    )

    sprints = relationship(
        "Sprint",
        back_populates="project"
    )

    meeting_notes = relationship(
        "MeetingNote",
        back_populates="project"
    )

    risk_reports = relationship(
        "RiskReport",
        back_populates="project"
    )

    github_repository = relationship(
        "GitHubRepository",
        back_populates="project"
    )