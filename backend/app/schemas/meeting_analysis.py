from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MeetingDecisionExtraction(BaseModel):
    decision: str = Field(min_length=1)


class MeetingActionItemExtraction(BaseModel):
    action_item: str = Field(min_length=1)
    assignee: str | None = None
    due_date: datetime | None = None


class MeetingBlockerExtraction(BaseModel):
    blocker: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"] | None = None


class MeetingRiskExtraction(BaseModel):
    risk: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"] | None = None


class MeetingAnalysisResult(BaseModel):
    decisions: list[MeetingDecisionExtraction] = Field(
        default_factory=list
    )
    action_items: list[MeetingActionItemExtraction] = Field(
        default_factory=list
    )
    blockers: list[MeetingBlockerExtraction] = Field(
        default_factory=list
    )
    risks: list[MeetingRiskExtraction] = Field(
        default_factory=list
    )