from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class LessonBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    subject: str = Field(..., min_length=2, max_length=100)
    difficulty_level: str = Field(default="beginner", min_length=2, max_length=50)
    key_concepts: list[str] = Field(default_factory=list)
    definitions: list[str] = Field(default_factory=list)
    formulas: list[str] = Field(default_factory=list)
    simplified_explanation: str = Field(default="", max_length=2000)


class LessonCreate(LessonBase):
    document_id: PydanticObjectId


class LessonUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    subject: str | None = Field(default=None, min_length=2, max_length=100)
    difficulty_level: str | None = Field(default=None, min_length=2, max_length=50)
    key_concepts: list[str] | None = None
    definitions: list[str] | None = None
    formulas: list[str] | None = None
    simplified_explanation: str | None = Field(default=None, min_length=2, max_length=2000)


class LessonRead(LessonBase):
    id: PydanticObjectId
    document_id: PydanticObjectId
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LessonList(BaseModel):
    lessons: list[LessonRead] = Field(default_factory=list)


class LessonGenerationRequest(BaseModel):
    document_id: PydanticObjectId
    target_level: str = Field(default="beginner", min_length=2, max_length=50)
    simple_language: bool = True
    include_examples: bool = True
    include_exercises: bool = False


class LessonGenerationResponse(BaseModel):
    lesson_plan_id: PydanticObjectId | None = None
    status: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=2, max_length=255)

    model_config = ConfigDict(from_attributes=True)


LessonResponse = LessonRead
LessonListResponse = LessonList
