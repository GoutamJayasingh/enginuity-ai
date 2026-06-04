from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.db.base import Base


class GitHubRepository(Base):
    __tablename__ = "github_repositories"

    id = Column(Integer, primary_key=True, index=True)

    repo_name = Column(String, nullable=False)

    repo_url = Column(String, nullable=False)

    description = Column(String)

    owner_name = Column(String)

    connected_at = Column(DateTime, default=datetime.utcnow)

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )