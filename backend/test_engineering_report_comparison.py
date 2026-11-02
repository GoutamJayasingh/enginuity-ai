import app.db.base_imports

from app.db.session import SessionLocal

from app.services.engineering_comparison_service import (
    compare_engineering_reports,
)


db = SessionLocal()

try:
    result = compare_engineering_reports(
        project_id=1,
        previous_report_id=2,
        latest_report_id=3,
        db=db,
    )

    print("\nENGINEERING REPORT COMPARISON")
    print("=============================")

    print(result.model_dump_json(indent=4))

finally:
    db.close()