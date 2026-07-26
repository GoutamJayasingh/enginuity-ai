from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueResponse
)
from app.services.issue_service import IssueService, assign_issue_to_sprint
from app.api.auth import get_current_user
from app.models.user import User

    
router = APIRouter(
    prefix="/issues",
    tags=["Issues"]
)


@router.post(
    "/sprints/{sprint_id}",
    response_model=IssueResponse
)
def create_issue(
    sprint_id: int,
    issue_data: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return IssueService.create_issue(
        db,
        sprint_id,
        issue_data
    )


@router.get(
    "/sprints/{sprint_id}",
    response_model=list[IssueResponse]
)
def get_all_issues(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return IssueService.get_all_issues(
        db,
        sprint_id
    )


@router.get(
    "/{issue_id}",
    response_model=IssueResponse
)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return IssueService.get_issue(
        db,
        issue_id
    )


@router.put(
    "/{issue_id}",
    response_model=IssueResponse
)
def update_issue(
    issue_id: int,
    issue_data: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return IssueService.update_issue(
        db,
        issue_id,
        issue_data
    )


@router.delete(
    "/{issue_id}"
)
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return IssueService.delete_issue(
        db,
        issue_id
    )

@router.patch("/{issue_id}/assign/{sprint_id}", response_model=IssueResponse)
def assign_issue_to_sprint_endpoint(
    issue_id: int,
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return assign_issue_to_sprint(
        issue_id,
        sprint_id,
        db
    )