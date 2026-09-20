from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.auth import get_current_user
from app.models.user import User

from app.services.meeting_service import (
    create_meeting_note,
    get_project_meeting_notes,
    get_meeting_note
)

router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_meeting(
    title: str,
    content: str,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_note = create_meeting_note(
        title=title,
        content=content,
        project_id=project_id,
        db=db
    )

    return {
        "message": "Meeting note created successfully.",
        "meeting_note": meeting_note
    }

@router.get(
    "/project/{project_id}"
)
def get_project_meetings(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_notes = get_project_meeting_notes(
        project_id=project_id,
        db=db
    )

    return {
        "project_id": project_id,
        "total_meetings": len(meeting_notes),
        "meeting_notes": meeting_notes
    }

@router.get(
    "/{meeting_note_id}"
)
def get_single_meeting(
    meeting_note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_note = get_meeting_note(
        meeting_note_id=meeting_note_id,
        db=db
    )

    return {
        "meeting_note": meeting_note
    }