from datetime import UTC, datetime

from beanie import Document, PydanticObjectId
from pydantic import Field


class ExtractedContent(Document):
    document_id: PydanticObjectId
    raw_text: str = ""
    cleaned_text: str = ""
    detected_formulas: list[str] = Field(default_factory=list)
    detected_diagrams: list[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "extracted_contents"
