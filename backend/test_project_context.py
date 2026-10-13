import app.db.base_imports

from app.db.session import SessionLocal
from app.services.project_context_service import (
    get_project_github_context,
)
from fastapi import HTTPException
import json
from datetime import datetime


def json_serializer(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


db = SessionLocal()

try:
    project_id = int(input("Enter an existing project ID: "))

    result = get_project_github_context(
        project_id=project_id,
        db=db,
    )

    print("\nProject context retrieved successfully:")
    print(json.dumps(
        result,
        default=json_serializer,
        indent=2,
    ))

except HTTPException as exc:
    print(f"HTTP error {exc.status_code}: {exc.detail}")

except Exception as exc:
    print(f"Test failed: {type(exc).__name__}: {exc}")

finally:
    db.close()
