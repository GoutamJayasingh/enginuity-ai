from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)

    github_id = Column(Integer, unique=True, nullable=False, index=True)

    number = Column(Integer, nullable=False)

    title = Column(String, nullable=False)

    description = Column(Text, nullable=True)

    state = Column(String, nullable=False)

    author_name = Column(String, nullable=True)

    author_url = Column(String, nullable=True)

    source_branch = Column(String, nullable=True)

    target_branch = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=True)

    updated_at = Column(DateTime, nullable=True)

    merged_at = Column(DateTime, nullable=True)

    merged = Column(Boolean, default=False)

    repository_id = Column(
        Integer,
        ForeignKey("github_repositories.id"),
        nullable=False
    )

    repository = relationship(
        "GitHubRepository",
        back_populates="pull_requests"
    )