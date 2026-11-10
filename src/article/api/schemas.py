from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CheckResultOut(BaseModel):
    id: str
    title: str
    status: str
    message: str
    weight: int = Field(default=1, ge=0)


class RunCreate(BaseModel):
    project_name: str = Field(min_length=1, max_length=255)
    charter_name: str = Field(min_length=1, max_length=255)
    charter_version: str = Field(min_length=1, max_length=100)
    score: float = Field(ge=0, le=100, allow_inf_nan=False)
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    skipped: int = Field(ge=0)
    results: list[CheckResultOut]


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_name: str
    charter_name: str = Field(min_length=1, max_length=255)
    charter_version: str = Field(min_length=1, max_length=100)
    score: float = Field(ge=0, le=100, allow_inf_nan=False)
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    skipped: int = Field(ge=0)
    results: list[CheckResultOut]
    created_at: datetime
