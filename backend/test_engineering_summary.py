
import app.db.base_imports

import json
from datetime import datetime

from fastapi import HTTPException

from app.db.session import SessionLocal
from app.services.engineering_summary_service import (
    build_engineering_summary,
)


def json_serializer(value):
    if isinstance(value, datetime):
        return value.isoformat()

    return str(value)


db = SessionLocal()

try:
    project_id = int(input("Enter an existing project ID: "))

    result = build_engineering_summary(
        project_id=project_id,
        db=db,
    )

    print("\nEngineering summary retrieved successfully:")
    print(
        json.dumps(
            result,
            default=json_serializer,
            indent=2,
        )
    )

except HTTPException as exc:
    print(f"HTTP error {exc.status_code}: {exc.detail}")

except Exception as exc:
    print(f"Test failed: {type(exc).__name__}: {exc}")

finally:
    db.close()
