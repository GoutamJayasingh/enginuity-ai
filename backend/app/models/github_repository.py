from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class GitHubRepository(Base):
    __tablename__ = "github_repositories"

    id = Column(Integer, primary_key=True, index=True)

    repo_name = Column(String, nullable=False)

    full_name = Column(String, nullable=False)

    repo_url = Column(String, nullable=False)

    description = Column(String)

    owner_name = Column(String)

    private = Column(Boolean, default=False)

    default_branch = Column(String)

    language = Column(String)

    stars = Column(Integer, default=0)

    forks = Column(Integer, default=0)

    connected_at = Column(DateTime, default=datetime.utcnow)

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship(
        "Project",
        back_populates="github_repository"
    )