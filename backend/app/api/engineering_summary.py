
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies.current_user import get_current_user
from app.models.project import Project
from app.models.user import User
from app.services.engineering_summary_service import (
    build_engineering_summary,
)

from fastapi import HTTPException, status


router = APIRouter(
    prefix="/projects",
    tags=["Engineering Summary"],
)


@router.get("/{project_id}/engineering-summary")
def get_engineering_summary(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return build_engineering_summary(
        project_id=project_id,
        db=db,
    )
