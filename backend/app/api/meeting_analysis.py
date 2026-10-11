from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.meeting_service import get_meeting_note
from app.services.meeting_analysis_service import (
    analyze_meeting_content,
    persist_meeting_decisions,
    persist_meeting_action_items,
    persist_meeting_blockers,
    persist_meeting_risks,
)

from app.models.meeting_decision import MeetingDecision
from app.models.meeting_action_item import MeetingActionItem
from app.models.meeting_blocker import MeetingBlocker
from app.models.meeting_risk import MeetingRisk


router = APIRouter(
    prefix="/meeting-analysis",
    tags=["AI Meeting Analysis"],
)


@router.post("/{meeting_note_id}/analyze")
def analyze_meeting(
    meeting_note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting_note = get_meeting_note(
        meeting_note_id=meeting_note_id,
        db=db,
    )

    if not meeting_note.content or not meeting_note.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting note has no content to analyze.",
        )
    if meeting_has_existing_intelligence(
        meeting_note_id=meeting_note_id,
        db=db,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This meeting already has decisions, action items, "
                "blockers, or risks. Re-analysis is disabled to "
                "prevent duplicate records."
            ),
        )

    result = analyze_meeting_content(
        meeting_content=meeting_note.content,
    )

    try:
        saved_decisions = persist_meeting_decisions(
            result=result,
            meeting_note_id=meeting_note_id,
            db=db,
        )

        saved_action_items = persist_meeting_action_items(
            result=result,
            meeting_note_id=meeting_note_id,
            db=db,
        )

        saved_blockers = persist_meeting_blockers(
            result=result,
            meeting_note_id=meeting_note_id,
            db=db,
        )

        saved_risks = persist_meeting_risks(
            result=result,
            meeting_note_id=meeting_note_id,
            db=db,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Meeting analysis completed successfully.",
        "meeting_note_id": meeting_note_id,
        "analysis": result,
        "saved_counts": {
            "decisions": len(saved_decisions),
            "action_items": len(saved_action_items),
            "blockers": len(saved_blockers),
            "risks": len(saved_risks),
        },
    }

def meeting_has_existing_intelligence(
    meeting_note_id: int,
    db: Session,
) -> bool:
    models = [
        MeetingDecision,
        MeetingActionItem,
        MeetingBlocker,
        MeetingRisk,
    ]

    for model in models:
        existing_record = (
            db.query(model.id)
            .filter(model.meeting_note_id == meeting_note_id)
            .first()
        )

        if existing_record:
            return True

    return False