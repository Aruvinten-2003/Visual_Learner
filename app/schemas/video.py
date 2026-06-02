from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class VideoBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    video_path: str = Field(..., min_length=1, max_length=500)
    transcript_path: str | None = Field(default=None, min_length=1, max_length=500)
    captions_path: str | None = Field(default=None, min_length=1, max_length=500)
    duration_seconds: float = Field(default=0.0, ge=0)


class VideoCreate(VideoBase):
    user_id: PydanticObjectId | None = None
    document_id: PydanticObjectId | None = None
    render_job_id: PydanticObjectId | None = None


class VideoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    video_path: str | None = Field(default=None, min_length=1, max_length=500)
    transcript_path: str | None = Field(default=None, min_length=1, max_length=500)
    captions_path: str | None = Field(default=None, min_length=1, max_length=500)
    duration_seconds: float | None = Field(default=None, ge=0)


class VideoRead(VideoBase):
    id: PydanticObjectId
    user_id: PydanticObjectId | None = None
    document_id: PydanticObjectId | None = None
    render_job_id: PydanticObjectId | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VideoList(BaseModel):
    videos: list[VideoRead] = Field(default_factory=list)
