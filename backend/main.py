from fastapi import FastAPI

import app.db.base_imports

from app.api.auth import router as auth_router

from app.api.project import router as project_router

from app.api.sprint import router as sprint_router

from app.api.issue import router as issue_router

from app.api.meeting import router as meeting_router

from app.api.meeting_decision import router as meeting_decision_router

from app.api.meeting_action_item import router as meeting_action_item_router

from app.api.meeting_blocker import router as meeting_blocker_router

from app.api import github

app = FastAPI()

app.include_router(auth_router)

app.include_router(project_router)

app.include_router(github.router)

app.include_router(sprint_router)

app.include_router(issue_router)

app.include_router(meeting_router)

app.include_router(meeting_decision_router)

app.include_router(meeting_action_item_router)

app.include_router(meeting_blocker_router)