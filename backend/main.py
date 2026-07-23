from fastapi import FastAPI

from app.api.auth import router as auth_router

from app.api.project import router as project_router

from app.api.sprint import router as sprint_router

from app.api import github

app = FastAPI()

app.include_router(auth_router)

app.include_router(project_router)

app.include_router(github.router)

app.include_router(sprint_router)