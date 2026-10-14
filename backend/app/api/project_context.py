
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies.current_user import get_current_user
from app.models.project import Project
from app.models.user import User
from app.services.project_context_service import (
    get_project_github_context
)

router = APIRouter()


@router.get("/projects/{project_id}/context")
def get_unified_project_context(
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return get_project_github_context(
        project_id=project_id,
        db=db
    )
