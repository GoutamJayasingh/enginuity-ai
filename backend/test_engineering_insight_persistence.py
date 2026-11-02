import app.db.base_imports

from app.db.session import SessionLocal
from app.models.engineering_insight import EngineeringInsight
from app.schemas.engineering_insights import EngineeringInsightsResult
from app.services.engineering_insights_service import (
    persist_engineering_insights,
)


db = SessionLocal()
test_report_id = None

try:
    test_insights = EngineeringInsightsResult(
        development_progress=[],
        blocker_analysis=[
            {
                "title": "Test blocker",
                "description": "Testing database persistence.",
                "evidence": ["Temporary persistence test."],
                "severity": "medium",
            }
        ],
        delivery_risks=[],
        recommendations=[],
    )

    saved_report = persist_engineering_insights(
        project_id=1,
        insights=test_insights,
        db=db,
    )

    test_report_id = saved_report.id

    retrieved_report = (
        db.query(EngineeringInsight)
        .filter(EngineeringInsight.id == test_report_id)
        .first()
    )

    print("\nPERSISTENCE TEST")
    print("================")

    print("Report ID:", retrieved_report.id)
    print("Project ID:", retrieved_report.project_id)
    print("Model:", retrieved_report.model_name)
    print("Prompt Version:", retrieved_report.prompt_version)
    print("Generated At:", retrieved_report.generated_at)
    print("Insights:", retrieved_report.insights)

finally:
    if test_report_id is not None:
        db.query(EngineeringInsight).filter(
            EngineeringInsight.id == test_report_id
        ).delete(synchronize_session=False)

        db.commit()
        print("\nTemporary test report cleaned up.")

    db.close()