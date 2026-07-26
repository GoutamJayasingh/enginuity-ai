from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.models.sprint import Sprint
from app.schemas.issue import IssueCreate, IssueUpdate


class IssueService:

    @staticmethod
    def create_issue(
        db: Session,
        sprint_id: int,
        issue_data: IssueCreate
    ) -> Issue:

        sprint = db.query(Sprint).filter(
            Sprint.id == sprint_id
        ).first()

        if not sprint:
            raise HTTPException(
                status_code=404,
                detail="Sprint not found."
            )

        issue = Issue(
            **issue_data.model_dump(),
            sprint_id=sprint_id
        )

        db.add(issue)
        db.commit()
        db.refresh(issue)

        return issue

    @staticmethod
    def get_all_issues(
        db: Session,
        sprint_id: int
    ):

        sprint = db.query(Sprint).filter(
            Sprint.id == sprint_id
        ).first()

        if not sprint:
            raise HTTPException(
                status_code=404,
                detail="Sprint not found."
            )

        return db.query(Issue).filter(
            Issue.sprint_id == sprint_id
        ).all()

    @staticmethod
    def get_issue(
        db: Session,
        issue_id: int
    ):

        issue = db.query(Issue).filter(
            Issue.id == issue_id
        ).first()

        if not issue:
            raise HTTPException(
                status_code=404,
                detail="Issue not found."
            )

        return issue

    @staticmethod
    def update_issue(
        db: Session,
        issue_id: int,
        issue_data: IssueUpdate
    ):

        issue = db.query(Issue).filter(
            Issue.id == issue_id
        ).first()

        if not issue:
            raise HTTPException(
                status_code=404,
                detail="Issue not found."
            )

        update_data = issue_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(issue, key, value)

        db.commit()
        db.refresh(issue)

        return issue

    @staticmethod
    def delete_issue(
        db: Session,
        issue_id: int
    ):

        issue = db.query(Issue).filter(
            Issue.id == issue_id
        ).first()

        if not issue:
            raise HTTPException(
                status_code=404,
                detail="Issue not found."
            )

        db.delete(issue)
        db.commit()

        return {
            "message": "Issue deleted successfully."
        }

def assign_issue_to_sprint(
    issue_id: int,
    sprint_id: int,
    db: Session
):
    issue = (
        db.query(Issue)
        .filter(Issue.id == issue_id)
        .first()
    )

    if not issue:
        raise HTTPException(
            status_code=404,
            detail="Issue not found."
        )

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

    issue.sprint_id = sprint_id

    db.commit()
    db.refresh(issue)

    return issue