from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CheckResultOut(BaseModel):
    id: str
    title: str
    status: str
    message: str
    weight: int = 1


class RunCreate(BaseModel):
    project_name: str = Field(min_length=1, max_length=255)
    charter_name: str
    charter_version: str
    score: float
    passed: int
    failed: int
    skipped: int
    results: list[CheckResultOut]


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_name: str
    charter_name: str
    charter_version: str
    score: float
    passed: int
    failed: int
    skipped: int
    results: list[CheckResultOut]
    created_at: datetime
