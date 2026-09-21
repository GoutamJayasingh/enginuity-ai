from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.meeting_decision import MeetingDecision

def create_meeting_decision(
    decision: str,
    meeting_note_id: int,
    db: Session
):
    meeting_decision = MeetingDecision(
        decision=decision,
        meeting_note_id=meeting_note_id
    )

    db.add(meeting_decision)
    db.commit()
    db.refresh(meeting_decision)

    return meeting_decision

def get_meeting_decisions(
    meeting_note_id: int,
    db: Session
):
    decisions = (
        db.query(MeetingDecision)
        .filter(
            MeetingDecision.meeting_note_id == meeting_note_id
        )
        .order_by(
            MeetingDecision.created_at.desc()
        )
        .all()
    )

    return decisions

def get_meeting_decision(
    meeting_decision_id: int,
    db: Session
):
    meeting_decision = (
        db.query(MeetingDecision)
        .filter(
            MeetingDecision.id == meeting_decision_id
        )
        .first()
    )

    if not meeting_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting decision not found."
        )

    return meeting_decision

