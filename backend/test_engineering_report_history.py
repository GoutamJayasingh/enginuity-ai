import app.db.base_imports

from app.db.session import SessionLocal
from app.models.engineering_insight import EngineeringInsight


db = SessionLocal()

try:
    reports = (
        db.query(EngineeringInsight)
        .filter(EngineeringInsight.project_id == 1)
        .order_by(EngineeringInsight.generated_at.asc())
        .all()
    )

    print("\nENGINEERING REPORT HISTORY")
    print("==========================")

    for report in reports:
        print(
            f"ID: {report.id} | "
            f"Project: {report.project_id} | "
            f"Generated: {report.generated_at}"
        )

    print("\nTotal reports:", len(reports))

finally:
    db.close()