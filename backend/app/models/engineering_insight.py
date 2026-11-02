from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class EngineeringInsight(Base):
    __tablename__ = "engineering_insights"

    id = Column(Integer, primary_key=True, index=True)

    insights = Column(JSON, nullable=False)

    model_name = Column(String, nullable=False)

    prompt_version = Column(String, nullable=False)

    generated_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="engineering_insights"
    )