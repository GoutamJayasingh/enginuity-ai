from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.auth import get_current_user
from app.models.user import User

from app.services.meeting_action_item_service import (
    create_meeting_action_item,
    get_meeting_action_items,
    get_meeting_action_item
)

router = APIRouter(
    prefix="/meeting-action-items",
    tags=["Meeting Action Items"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_action_item(
    action_item: str,
    meeting_note_id: int,
    assignee: str | None = None,
    due_date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_action_item = create_meeting_action_item(
        action_item=action_item,
        assignee=assignee,
        due_date=due_date,
        meeting_note_id=meeting_note_id,
        db=db
    )

    return {
        "message": "Meeting action item created successfully.",
        "meeting_action_item": meeting_action_item
    }


@router.get("/meeting/{meeting_note_id}")
def get_action_items_for_meeting(
    meeting_note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    action_items = get_meeting_action_items(
        meeting_note_id=meeting_note_id,
        db=db
    )

    return {
        "meeting_note_id": meeting_note_id,
        "total_action_items": len(action_items),
        "action_items": action_items
    }


@router.get("/{meeting_action_item_id}")
def get_single_action_item(
    meeting_action_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_action_item = get_meeting_action_item(
        meeting_action_item_id=meeting_action_item_id,
        db=db
    )

    return {
        "meeting_action_item": meeting_action_item
    }