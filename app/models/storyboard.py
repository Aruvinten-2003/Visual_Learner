from datetime import UTC, datetime

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class Scene(BaseModel):
    scene_id: str
    scene_type: str
    title: str
    visual_description: str = ""
    narration_text: str = ""
    caption_text: str = ""
    duration_seconds: float = 0.0


class Storyboard(Document):
    lesson_plan_id: PydanticObjectId
    scenes: list[Scene] = Field(default_factory=list)
    narration_script: str = ""
    status: str = "draft"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "storyboards"
