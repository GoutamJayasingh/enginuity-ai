from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.meeting_action_item import MeetingActionItem


def create_meeting_action_item(
    action_item: str,
    assignee: str | None,
    due_date,
    meeting_note_id: int,
    db: Session
):
    meeting_action_item = MeetingActionItem(
        action_item=action_item,
        assignee=assignee,
        due_date=due_date,
        meeting_note_id=meeting_note_id
    )

    db.add(meeting_action_item)
    db.commit()
    db.refresh(meeting_action_item)

    return meeting_action_item


def get_meeting_action_items(
    meeting_note_id: int,
    db: Session
):
    action_items = (
        db.query(MeetingActionItem)
        .filter(
            MeetingActionItem.meeting_note_id == meeting_note_id
        )
        .order_by(MeetingActionItem.created_at.desc())
        .all()
    )

    return action_items


def get_meeting_action_item(
    meeting_action_item_id: int,
    db: Session
):
    meeting_action_item = (
        db.query(MeetingActionItem)
        .filter(
            MeetingActionItem.id == meeting_action_item_id
        )
        .first()
    )

    if not meeting_action_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting action item not found."
        )

    return meeting_action_item