from datetime import UTC, datetime

from beanie import Document, PydanticObjectId
from pydantic import Field


class Video(Document):
    user_id: PydanticObjectId | None = None
    document_id: PydanticObjectId | None = None
    render_job_id: PydanticObjectId | None = None
    title: str
    video_path: str
    transcript_path: str | None = None
    captions_path: str | None = None
    duration_seconds: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "videos"
