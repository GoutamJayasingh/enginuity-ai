from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.core.security import get_current_user

from app.models.user import User

from app.schemas.sprint import (
    SprintCreate,
    SprintUpdate,
    SprintResponse
)

from app.services.sprint_service import (
    create_sprint,
    get_project_sprints,
    get_sprint_by_id,
    update_sprint,
    delete_sprint
)

router = APIRouter(
    prefix="/sprints",
    tags=["Sprint Management"]
)

@router.post(
    "/projects/{project_id}",
    response_model=SprintResponse
)
def create_new_sprint(
    project_id: int,
    sprint: SprintCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_sprint(
        project_id=project_id,
        sprint=sprint,
        db=db
    )

@router.get(
    "/projects/{project_id}",
    response_model=list[SprintResponse]
)
def get_sprints(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_project_sprints(
        project_id,
        db
    )

@router.get(
    "/{sprint_id}",
    response_model=SprintResponse
)
def get_sprint(
    sprint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_sprint_by_id(
        sprint_id,
        db
    )

@router.put(
    "/{sprint_id}",
    response_model=SprintResponse
)
def update_existing_sprint(
    sprint_id: int,
    sprint_update: SprintUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_sprint(
        sprint_id,
        sprint_update,
        db
    )

@router.delete("/{sprint_id}")
def remove_sprint(
    sprint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_sprint(
        sprint_id,
        db
    )


