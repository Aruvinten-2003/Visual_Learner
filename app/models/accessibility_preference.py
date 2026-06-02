from datetime import UTC, datetime

from beanie import Document, PydanticObjectId
from pydantic import Field


class AccessibilityPreference(Document):
    user_id: PydanticObjectId
    font_size: str = "medium"
    dyslexia_font: bool = False
    high_contrast: bool = False
    narration_speed: float = 1.0
    simple_language: bool = True
    captions_enabled: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "accessibility_preferences"
