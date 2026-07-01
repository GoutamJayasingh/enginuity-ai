from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate
)
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

@router.get("/projects/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        return {
            "message": "Project not found"
        }

    return project

@router.put("/projects/{project_id}")
def update_project(
    project_id: int,
    updated_project: ProjectUpdate,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        return {
            "message": "Project not found"
        }

    project.name = updated_project.name
    project.description = updated_project.description

    db.commit()

    db.refresh(project)

    return project

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        return {
            "message": "Project not found"
        }

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }