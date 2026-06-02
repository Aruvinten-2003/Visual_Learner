from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class RenderJobCreate(BaseModel):
    storyboard_id: PydanticObjectId


class RenderJobUpdate(BaseModel):
    job_status: str | None = Field(default=None, min_length=1, max_length=50)
    progress: int | None = Field(default=None, ge=0, le=100)
    error_message: str | None = Field(default=None, max_length=1000)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class RenderJobRead(BaseModel):
    id: PydanticObjectId
    storyboard_id: PydanticObjectId
    job_status: str
    progress: int
    error_message: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RenderJobList(BaseModel):
    render_jobs: list[RenderJobRead] = Field(default_factory=list)
