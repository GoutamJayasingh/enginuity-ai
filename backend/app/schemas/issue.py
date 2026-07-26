from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = None
    issue_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = "open"


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class IssueResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    issue_type: Optional[str]
    priority: Optional[str]
    status: str
    created_at: datetime
    sprint_id: Optional[int]

    model_config = {
        "from_attributes": True
    }