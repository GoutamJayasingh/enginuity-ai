from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class RiskReport(Base):
    __tablename__ = "risk_reports"

    id = Column(Integer, primary_key=True, index=True)

    risk_score = Column(Integer)

    risk_level = Column(String)

    prediction = Column(String)

    reason = Column(String)

    generated_at = Column(DateTime, default=datetime.utcnow)

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship(
        "Project",
        back_populates="risk_reports"
    )