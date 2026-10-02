from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.auth import get_current_user
from app.models.user import User

from app.services.meeting_risk_service import (
    create_meeting_risk,
    get_meeting_risks,
    get_meeting_risk
)


router = APIRouter(
    prefix="/meeting-risks",
    tags=["Meeting Risks"]
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_risk(
    risk: str,
    meeting_note_id: int,
    severity: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_risk = create_meeting_risk(
        risk=risk,
        severity=severity,
        meeting_note_id=meeting_note_id,
        db=db
    )

    return {
        "message": "Meeting risk created successfully.",
        "meeting_risk": meeting_risk
    }


@router.get("/meeting/{meeting_note_id}")
def get_risks_for_meeting(
    meeting_note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    risks = get_meeting_risks(
        meeting_note_id=meeting_note_id,
        db=db
    )

    return {
        "meeting_note_id": meeting_note_id,
        "total_risks": len(risks),
        "risks": risks
    }


@router.get("/{meeting_risk_id}")
def get_single_risk(
    meeting_risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_risk = get_meeting_risk(
        meeting_risk_id=meeting_risk_id,
        db=db
    )

    return {
        "meeting_risk": meeting_risk
    }