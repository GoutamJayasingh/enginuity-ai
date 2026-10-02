from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.auth import get_current_user
from app.models.user import User

from app.services.meeting_intelligence_service import (
    get_meeting_intelligence
)


router = APIRouter(
    prefix="/meeting-intelligence",
    tags=["Meeting Intelligence"]
)


@router.get("/{meeting_note_id}")
def get_meeting_intelligence_summary(
    meeting_note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    intelligence = get_meeting_intelligence(
        meeting_note_id=meeting_note_id,
        db=db
    )

    return intelligence