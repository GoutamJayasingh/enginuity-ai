import app.db.base_imports

from sqlalchemy.orm import configure_mappers

from app.models.project import Project
from app.models.engineering_insight import EngineeringInsight


try:
    configure_mappers()

    print("SQLAlchemy relationships configured successfully.")

    print(
        "Project relationship:",
        Project.engineering_insights.property.mapper.class_.__name__
    )

    print(
        "EngineeringInsight relationship:",
        EngineeringInsight.project.property.mapper.class_.__name__
    )

except Exception as error:
    print("Model relationship validation failed:")
    print(error)