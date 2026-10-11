from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.meeting_risk import MeetingRisk


def create_meeting_risk(
    risk: str,
    severity: str | None,
    meeting_note_id: int,
    db: Session,
    commit: bool = True,
):
    meeting_risk = MeetingRisk(
        risk=risk,
        severity=severity,
        meeting_note_id=meeting_note_id,
    )

    db.add(meeting_risk)

    if commit:
        db.commit()
        db.refresh(meeting_risk)
    else:
        db.flush()

    return meeting_risk


def get_meeting_risks(
    meeting_note_id: int,
    db: Session
):
    risks = (
        db.query(MeetingRisk)
        .filter(
            MeetingRisk.meeting_note_id == meeting_note_id
        )
        .order_by(MeetingRisk.created_at.desc())
        .all()
    )

    return risks


def get_meeting_risk(
    meeting_risk_id: int,
    db: Session
):
    meeting_risk = (
        db.query(MeetingRisk)
        .filter(
            MeetingRisk.id == meeting_risk_id
        )
        .first()
    )

    if not meeting_risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting risk not found."
        )

    return meeting_risk