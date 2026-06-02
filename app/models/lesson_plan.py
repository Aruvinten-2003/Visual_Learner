from datetime import UTC, datetime

from beanie import Document, PydanticObjectId
from pydantic import Field


class LessonPlan(Document):
    document_id: PydanticObjectId
    title: str
    subject: str
    difficulty_level: str = "beginner"
    key_concepts: list[str] = Field(default_factory=list)
    definitions: list[str] = Field(default_factory=list)
    formulas: list[str] = Field(default_factory=list)
    simplified_explanation: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "lesson_plans"
