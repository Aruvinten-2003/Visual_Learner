from datetime import UTC, datetime

from beanie import Document, PydanticObjectId
from pydantic import Field


class MediaAsset(Document):
    render_job_id: PydanticObjectId | None = None
    asset_type: str
    file_path: str
    mime_type: str = ""
    duration_seconds: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "media_assets"
