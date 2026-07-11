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
from app.models.user import User
from app.dependencies.current_user import get_current_user

router = APIRouter()

@router.post("/projects")
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_project = Project(
    name=project.name,
    description=project.description,
    owner_id=current_user.id
)

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return {
        "message": "Project created successfully"
    }

@router.get("/projects")
def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    projects = (
        db.query(Project)
        .filter(Project.owner_id == current_user.id)
        .all()
    )

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.owner_id == current_user.id
        )
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.owner_id == current_user.id
        )
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