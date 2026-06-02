from datetime import UTC, datetime

from beanie import Document, PydanticObjectId
from pydantic import Field


class LearningDocument(Document):
    user_id: PydanticObjectId | None = None
    title: str
    input_type: str
    subject: str
    file_path: str | None = None
    status: str = "uploaded"
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "documents"
