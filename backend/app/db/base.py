from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

from app.models.user import User
from app.models.project import Project
from app.models.issue import Issue
from app.models.github_repository import GitHubRepository
from app.models.commit import Commit
from app.models.meeting_note import MeetingNote
from app.models.risk_report import RiskReport
from app.models.sprint import Sprint