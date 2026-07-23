from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class SprintBase(BaseModel):
    name: str
    goal: Optional[str] = None
    start_date: date
    end_date: date
    status: Optional[str] = "Planned"

class SprintCreate(SprintBase):
    pass

class SprintResponse(SprintBase):
    id: int
    created_at: datetime
    project_id: int

    model_config = ConfigDict(from_attributes=True)