from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.auth import get_current_user
from app.models.user import User

from app.services.meeting_blocker_service import (
    create_meeting_blocker,
    get_meeting_blockers,
    get_meeting_blocker
)


router = APIRouter(
    prefix="/meeting-blockers",
    tags=["Meeting Blockers"]
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_blocker(
    blocker: str,
    meeting_note_id: int,
    severity: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_blocker = create_meeting_blocker(
        blocker=blocker,
        severity=severity,
        meeting_note_id=meeting_note_id,
        db=db
    )

    return {
        "message": "Meeting blocker created successfully.",
        "meeting_blocker": meeting_blocker
    }


@router.get("/meeting/{meeting_note_id}")
def get_blockers_for_meeting(
    meeting_note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    blockers = get_meeting_blockers(
        meeting_note_id=meeting_note_id,
        db=db
    )

    return {
        "meeting_note_id": meeting_note_id,
        "total_blockers": len(blockers),
        "blockers": blockers
    }


@router.get("/{meeting_blocker_id}")
def get_single_blocker(
    meeting_blocker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_blocker = get_meeting_blocker(
        meeting_blocker_id=meeting_blocker_id,
        db=db
    )

    return {
        "meeting_blocker": meeting_blocker
    }