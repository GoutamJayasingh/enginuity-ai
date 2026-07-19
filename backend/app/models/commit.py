from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Commit(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)

    sha = Column(String, unique=True, nullable=False)

    message = Column(Text, nullable=False)

    author_name = Column(String, nullable=False)

    author_email = Column(String, nullable=False)

    committed_at = Column(DateTime, nullable=False)

    repository_id = Column(
        Integer,
        ForeignKey("github_repositories.id"),
        nullable=False
    )

    repository = relationship(
        "GitHubRepository",
        back_populates="commits"
    )