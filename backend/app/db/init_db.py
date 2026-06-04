from app.db.base import Base
from app.db.session import engine

from app.models.user import User
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.issue import Issue
from app.models.meeting_note import MeetingNote
from app.models.risk_report import RiskReport
from app.models.github_repository import GitHubRepository

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()