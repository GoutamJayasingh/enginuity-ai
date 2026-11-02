from app.schemas.engineering_insights import EngineeringFinding

from pydantic import BaseModel, Field


class FindingChanges(BaseModel):
    newly_introduced: list[EngineeringFinding] = Field(
        default_factory=list
    )

    resolved: list[EngineeringFinding] = Field(
        default_factory=list
    )

    persistent: list[EngineeringFinding] = Field(
        default_factory=list
    )


class EngineeringComparisonResult(BaseModel):
    previous_report_id: int

    latest_report_id: int

    blocker_changes: FindingChanges = Field(
        default_factory=FindingChanges
    )

    risk_changes: FindingChanges = Field(
        default_factory=FindingChanges
    )

    recommendation_changes: FindingChanges = Field(
        default_factory=FindingChanges
    )

    development_progress_changes: FindingChanges = Field(
        default_factory=FindingChanges
    )