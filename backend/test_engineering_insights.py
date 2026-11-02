import app.db.base_imports

from app.db.session import SessionLocal
from app.services.engineering_insights_service import (
    generate_engineering_insights,
)


db = SessionLocal()

try:
    insights = generate_engineering_insights(
        project_id=1,
        db=db,
    )

    print("\nENGINEERING INSIGHTS")
    print("====================")

    print(insights.model_dump_json(indent=4))

except Exception as error:
    print("Engineering insights generation failed:")
    print(error)

finally:
    db.close()