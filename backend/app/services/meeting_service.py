from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.meeting_note import MeetingNote

def create_meeting_note(
    title: str,
    content: str,
    project_id: int,
    db: Session
):
    meeting_note = MeetingNote(
        title=title,
        content=content,
        project_id=project_id
    )

    db.add(meeting_note)
    db.commit()
    db.refresh(meeting_note)

    return meeting_note

def get_project_meeting_notes(
    project_id: int,
    db: Session
):
    meeting_notes = (
        db.query(MeetingNote)
        .filter(
            MeetingNote.project_id == project_id
        )
        .order_by(
            MeetingNote.created_at.desc()
        )
        .all()
    )

    return meeting_notes

def get_meeting_note(
    meeting_note_id: int,
    db: Session
):
    meeting_note = (
        db.query(MeetingNote)
        .filter(
            MeetingNote.id == meeting_note_id
        )
        .first()
    )

    if not meeting_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found."
        )

    return meeting_note