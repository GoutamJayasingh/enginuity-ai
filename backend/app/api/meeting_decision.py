from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.auth import get_current_user
from app.models.user import User

from app.services.meeting_decision_service import (
    create_meeting_decision,
    get_meeting_decisions,
    get_meeting_decision
)

router = APIRouter(
    prefix="/meeting-decisions",
    tags=["Meeting Decisions"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_decision(
    decision: str,
    meeting_note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_decision = create_meeting_decision(
        decision=decision,
        meeting_note_id=meeting_note_id,
        db=db
    )

    return {
        "message": "Meeting decision created successfully.",
        "meeting_decision": meeting_decision
    }

@router.get(
    "/meeting/{meeting_note_id}"
)
def get_decisions_for_meeting(
    meeting_note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decisions = get_meeting_decisions(
        meeting_note_id=meeting_note_id,
        db=db
    )

    return {
        "meeting_note_id": meeting_note_id,
        "total_decisions": len(decisions),
        "decisions": decisions
    }

@router.get(
    "/{meeting_decision_id}"
)
def get_single_decision(
    meeting_decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_decision = get_meeting_decision(
        meeting_decision_id=meeting_decision_id,
        db=db
    )

    return {
        "meeting_decision": meeting_decision
    }