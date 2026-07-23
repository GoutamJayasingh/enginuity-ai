from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.project import Project
from app.models.sprint import Sprint

from app.schemas.sprint import (
    SprintCreate,
    SprintUpdate
)

def create_sprint(
    project_id: int,
    sprint: SprintCreate,
    db: Session
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )

    new_sprint = Sprint(
        **sprint.model_dump(),
        project_id=project_id
    )

    db.add(new_sprint)
    db.commit()
    db.refresh(new_sprint)

    return new_sprint

def get_project_sprints(
    project_id: int,
    db: Session
):
    return (
        db.query(Sprint)
        .filter(Sprint.project_id == project_id)
        .all()
    )

def get_sprint_by_id(
    sprint_id: int,
    db: Session
):
    sprint = (
        db.query(Sprint)
        .filter(Sprint.id == sprint_id)
        .first()
    )

    if not sprint:
        raise HTTPException(
            status_code=404,
            detail="Sprint not found."
        )

    return sprint

def update_sprint(
    sprint_id: int,
    sprint_update: SprintUpdate,
    db: Session
):
    sprint = get_sprint_by_id(
        sprint_id,
        db
    )

    update_data = sprint_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            sprint,
            key,
            value
        )

    db.commit()
    db.refresh(sprint)

    return sprint

def delete_sprint(
    sprint_id: int,
    db: Session
):
    sprint = get_sprint_by_id(
        sprint_id,
        db
    )

    db.delete(sprint)
    db.commit()

    return {
        "message": "Sprint deleted successfully."
    }
