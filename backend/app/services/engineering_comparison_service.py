from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.engineering_insight import EngineeringInsight

from app.schemas.engineering_insights import EngineeringFinding
from app.schemas.engineering_comparison import (
    EngineeringComparisonResult,
    FindingChanges,
)


def normalize_finding(value: str) -> str:
    return " ".join(value.split()).casefold()


def compare_finding_categories(
    previous_findings: list[dict],
    latest_findings: list[dict],
) -> FindingChanges:

    previous_map = {
        normalize_finding(item["title"]): item
        for item in previous_findings
    }

    latest_map = {
        normalize_finding(item["title"]): item
        for item in latest_findings
    }

    previous_keys = set(previous_map.keys())
    latest_keys = set(latest_map.keys())

    newly_introduced = [
        EngineeringFinding.model_validate(latest_map[key])
        for key in latest_keys - previous_keys
    ]

    resolved = [
        EngineeringFinding.model_validate(previous_map[key])
        for key in previous_keys - latest_keys
    ]

    persistent = [
        EngineeringFinding.model_validate(latest_map[key])
        for key in previous_keys & latest_keys
    ]

    return FindingChanges(
        newly_introduced=newly_introduced,
        resolved=resolved,
        persistent=persistent,
    )


def compare_engineering_reports(
    project_id: int,
    previous_report_id: int,
    latest_report_id: int,
    db: Session,
) -> EngineeringComparisonResult:

    if previous_report_id == latest_report_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot compare a report with itself.",
        )

    reports = (
        db.query(EngineeringInsight)
        .filter(
            EngineeringInsight.project_id == project_id,
            EngineeringInsight.id.in_([
                previous_report_id,
                latest_report_id,
            ]),
        )
        .all()
    )

    reports_by_id = {
        report.id: report
        for report in reports
    }

    previous_report = reports_by_id.get(previous_report_id)
    latest_report = reports_by_id.get(latest_report_id)

    if not previous_report or not latest_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both engineering insight reports were not found.",
        )

    previous_insights = previous_report.insights
    latest_insights = latest_report.insights

    return EngineeringComparisonResult(
        previous_report_id=previous_report_id,
        latest_report_id=latest_report_id,

        blocker_changes=compare_finding_categories(
            previous_insights.get("blocker_analysis", []),
            latest_insights.get("blocker_analysis", []),
        ),

        risk_changes=compare_finding_categories(
            previous_insights.get("delivery_risks", []),
            latest_insights.get("delivery_risks", []),
        ),

        recommendation_changes=compare_finding_categories(
            previous_insights.get("recommendations", []),
            latest_insights.get("recommendations", []),
        ),

        development_progress_changes=compare_finding_categories(
            previous_insights.get("development_progress", []),
            latest_insights.get("development_progress", []),
        ),
    )