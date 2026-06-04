from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.db.base import Base


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    goal = Column(String)

    start_date = Column(DateTime)

    end_date = Column(DateTime)

    status = Column(String, default="planned")

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )