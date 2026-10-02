from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.meeting_note import MeetingNote
from app.models.meeting_decision import MeetingDecision
from app.models.meeting_action_item import MeetingActionItem
from app.models.meeting_blocker import MeetingBlocker
from app.models.meeting_risk import MeetingRisk


def get_meeting_intelligence(
    meeting_note_id: int,
    db: Session
):
    meeting_note = (
        db.query(MeetingNote)
        .filter(MeetingNote.id == meeting_note_id)
        .first()
    )

    if not meeting_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting note not found."
        )

    decisions = (
        db.query(MeetingDecision)
        .filter(
            MeetingDecision.meeting_note_id == meeting_note_id
        )
        .order_by(MeetingDecision.created_at.desc())
        .all()
    )

    action_items = (
        db.query(MeetingActionItem)
        .filter(
            MeetingActionItem.meeting_note_id == meeting_note_id
        )
        .order_by(MeetingActionItem.created_at.desc())
        .all()
    )

    blockers = (
        db.query(MeetingBlocker)
        .filter(
            MeetingBlocker.meeting_note_id == meeting_note_id
        )
        .order_by(MeetingBlocker.created_at.desc())
        .all()
    )

    risks = (
        db.query(MeetingRisk)
        .filter(
            MeetingRisk.meeting_note_id == meeting_note_id
        )
        .order_by(MeetingRisk.created_at.desc())
        .all()
    )

    return {
        "meeting_note": meeting_note,
        "decisions": decisions,
        "action_items": action_items,
        "blockers": blockers,
        "risks": risks
    }