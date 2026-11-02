from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies.current_user import get_current_user
from app.models.project import Project
from app.models.user import User
from app.services.engineering_insights_service import (
    generate_engineering_insights,
    persist_engineering_insights,
)
from app.models.engineering_insight import EngineeringInsight

from app.services.engineering_comparison_service import (
    compare_engineering_reports,
)

router = APIRouter(
    prefix="/projects",
    tags=["Engineering Insights"],
)


@router.post("/{project_id}/engineering-insights")
def create_engineering_insights(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Step 1: Verify project ownership
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Step 2: Generate AI engineering insights
    insights = generate_engineering_insights(
        project_id=project_id,
        db=db,
    )

    # Step 3: Persist the generated insights
    saved_report = persist_engineering_insights(
        project_id=project_id,
        insights=insights,
        db=db,
    )

    # Step 4: Return the saved report
    return {
        "id": saved_report.id,
        "project_id": saved_report.project_id,
        "insights": saved_report.insights,
        "model_name": saved_report.model_name,
        "prompt_version": saved_report.prompt_version,
        "generated_at": saved_report.generated_at,
    }

@router.get("/{project_id}/engineering-insights")
def get_engineering_insights_history(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Step 1: Verify project ownership
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Step 2: Retrieve historical reports
    reports = (
        db.query(EngineeringInsight)
        .filter(
            EngineeringInsight.project_id == project_id
        )
        .order_by(
            EngineeringInsight.generated_at.desc()
        )
        .all()
    )

    # Step 3: Return report history
    return [
        {
            "id": report.id,
            "project_id": report.project_id,
            "insights": report.insights,
            "model_name": report.model_name,
            "prompt_version": report.prompt_version,
            "generated_at": report.generated_at,
        }
        for report in reports
    ]

@router.get("/{project_id}/engineering-insights/compare")
def compare_project_engineering_insights(
    project_id: int,
    previous_report_id: int,
    latest_report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    comparison = compare_engineering_reports(
        project_id=project_id,
        previous_report_id=previous_report_id,
        latest_report_id=latest_report_id,
        db=db,
    )

    return comparison