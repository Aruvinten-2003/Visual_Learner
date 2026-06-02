from datetime import UTC, datetime

from beanie import Document, PydanticObjectId
from pydantic import Field


class RenderJob(Document):
    storyboard_id: PydanticObjectId
    job_status: str = "queued"
    progress: int = 0
    error_message: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "render_jobs"
