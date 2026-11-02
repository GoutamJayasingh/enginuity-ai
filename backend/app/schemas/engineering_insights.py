from pydantic import BaseModel, Field


class EngineeringFinding(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        description="A short title describing the finding."
    )

    description: str = Field(
        ...,
        min_length=1,
        description="An explanation of the finding."
    )

    evidence: list[str] = Field(
        ...,
        min_length=1,
        description="Facts from the project context supporting this finding."
    )

    severity: str = Field(
        ...,
        description="The importance level: low, medium, or high."
    )


class EngineeringInsightsResult(BaseModel):
    development_progress: list[EngineeringFinding] = Field(
        default_factory=list
    )

    blocker_analysis: list[EngineeringFinding] = Field(
        default_factory=list
    )

    delivery_risks: list[EngineeringFinding] = Field(
        default_factory=list
    )

    recommendations: list[EngineeringFinding] = Field(
        default_factory=list
    )