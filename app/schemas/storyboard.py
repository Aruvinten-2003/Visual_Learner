from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class SceneBase(BaseModel):
    scene_id: str = Field(..., min_length=1, max_length=100)
    scene_type: str = Field(..., min_length=2, max_length=100)
    title: str = Field(..., min_length=2, max_length=255)
    visual_description: str = Field(default="", max_length=1000)
    narration_text: str = Field(default="", max_length=2000)
    caption_text: str = Field(default="", max_length=1000)
    duration_seconds: float = Field(default=0.0, ge=0)


class SceneCreate(SceneBase):
    pass


class SceneUpdate(BaseModel):
    scene_type: str | None = Field(default=None, min_length=2, max_length=100)
    title: str | None = Field(default=None, min_length=2, max_length=255)
    visual_description: str | None = Field(default=None, max_length=1000)
    narration_text: str | None = Field(default=None, max_length=2000)
    caption_text: str | None = Field(default=None, max_length=1000)
    duration_seconds: float | None = Field(default=None, ge=0)


class SceneRead(SceneBase):
    pass


class StoryboardBase(BaseModel):
    scenes: list[SceneBase] = Field(default_factory=list)
    narration_script: str = Field(default="", max_length=5000)
    status: str = Field(default="draft", min_length=1, max_length=50)


class StoryboardCreate(StoryboardBase):
    lesson_plan_id: PydanticObjectId


class StoryboardUpdate(BaseModel):
    scenes: list[SceneBase] | None = None
    narration_script: str | None = Field(default=None, max_length=5000)
    status: str | None = Field(default=None, min_length=1, max_length=50)


class StoryboardRead(StoryboardBase):
    id: PydanticObjectId
    lesson_plan_id: PydanticObjectId
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StoryboardList(BaseModel):
    storyboards: list[StoryboardRead] = Field(default_factory=list)
