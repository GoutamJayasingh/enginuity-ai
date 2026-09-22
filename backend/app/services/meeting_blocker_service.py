from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.meeting_blocker import MeetingBlocker


def create_meeting_blocker(
    blocker: str,
    severity: str | None,
    meeting_note_id: int,
    db: Session
):
    meeting_blocker = MeetingBlocker(
        blocker=blocker,
        severity=severity,
        meeting_note_id=meeting_note_id
    )

    db.add(meeting_blocker)
    db.commit()
    db.refresh(meeting_blocker)

    return meeting_blocker


def get_meeting_blockers(
    meeting_note_id: int,
    db: Session
):
    blockers = (
        db.query(MeetingBlocker)
        .filter(
            MeetingBlocker.meeting_note_id == meeting_note_id
        )
        .order_by(MeetingBlocker.created_at.desc())
        .all()
    )

    return blockers


def get_meeting_blocker(
    meeting_blocker_id: int,
    db: Session
):
    meeting_blocker = (
        db.query(MeetingBlocker)
        .filter(
            MeetingBlocker.id == meeting_blocker_id
        )
        .first()
    )

    if not meeting_blocker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting blocker not found."
        )

    return meeting_blocker