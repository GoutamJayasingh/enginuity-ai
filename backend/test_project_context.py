
import app.db.base_imports

import json
from datetime import datetime

from fastapi import HTTPException

from app.db.session import SessionLocal
from app.models.meeting_blocker import MeetingBlocker
from app.services.project_context_service import (
    get_project_github_context,
)


def json_serializer(value):
    if isinstance(value, datetime):
        return value.isoformat()

    return str(value)


db = SessionLocal()

try:
    project_id = int(input("Enter an existing project ID: "))

    # Retrieve and display the unified project context.
    result = get_project_github_context(
        project_id=project_id,
        db=db,
    )

    print("\nProject context retrieved successfully:")
    print(
        json.dumps(
            result,
            default=json_serializer,
            indent=2,
        )
    )

    # Inspect existing blocker records for meeting ID 1.
    meeting_note_id = 1

    blockers = (
        db.query(MeetingBlocker)
        .filter(
            MeetingBlocker.meeting_note_id == meeting_note_id
        )
        .order_by(MeetingBlocker.id.asc())
        .all()
    )

    print("\nBlockers stored for meeting:", meeting_note_id)

    for blocker in blockers:
        print({
            "id": blocker.id,
            "blocker": blocker.blocker,
            "severity": blocker.severity,
            "status": blocker.status,
            "meeting_note_id": blocker.meeting_note_id,
        })

except HTTPException as exc:
    print(f"HTTP error {exc.status_code}: {exc.detail}")

except Exception as exc:
    print(f"Test failed: {type(exc).__name__}: {exc}")

finally:
    db.close()
