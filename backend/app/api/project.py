from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.project import ProjectCreate
from app.models.project import Project

router = APIRouter()

@router.post("/projects")
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    new_project = Project(
        name=project.name,
        description=project.description
    )

    db.add(new_project)
    db.commit()

    return {
        "message": "Project created successfully"
    }

@router.get("/projects")
def get_projects(
    db: Session = Depends(get_db)
):
    projects = db.query(Project).all()

    return projects