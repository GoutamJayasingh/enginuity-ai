from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.meeting_blocker import MeetingBlocker


def create_meeting_blocker(
    blocker: str,
    severity: str | None,
    meeting_note_id: int,
    db: Session,
    commit: bool = True,
):
    normalized_blocker = " ".join(blocker.split()).casefold()

    existing_blockers = (
        db.query(MeetingBlocker)
        .filter(
            MeetingBlocker.meeting_note_id == meeting_note_id,
            MeetingBlocker.status == "open",
        )
        .all()
    )

    for existing_blocker in existing_blockers:
        existing_description = " ".join(
            existing_blocker.blocker.split()
        ).casefold()

        if existing_description == normalized_blocker:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An active blocker with the same description "
                    "already exists for this meeting."
                ),
            )

    meeting_blocker = MeetingBlocker(
        blocker=blocker.strip(),
        severity=severity,
        meeting_note_id=meeting_note_id,
    )

    db.add(meeting_blocker)

    if commit:
        try:
            db.commit()
            db.refresh(meeting_blocker)
        except Exception:
            db.rollback()
            raise
    else:
        db.flush()

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