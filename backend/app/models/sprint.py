from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    goal = Column(String)

    start_date = Column(
       Date, 
       nullable=False,
    )

    end_date = Column(
        Date,
        nullable=False,
    )

    status = Column(String, default="Planned")

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    project = relationship(
        "Project",
        back_populates="sprints"
    )

    issues = relationship(
        "Issue",
        back_populates="sprint"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )