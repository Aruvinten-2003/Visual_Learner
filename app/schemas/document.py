from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    input_type: str = Field(..., min_length=1, max_length=50)
    subject: str = Field(..., min_length=2, max_length=100)
    file_path: str | None = Field(default=None, min_length=1, max_length=500)


class DocumentCreate(DocumentBase):
    user_id: PydanticObjectId | None = None


class DocumentUploadRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    input_type: str = Field(..., min_length=1, max_length=50)
    subject: str = Field(..., min_length=2, max_length=100)


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    input_type: str | None = Field(default=None, min_length=1, max_length=50)
    subject: str | None = Field(default=None, min_length=2, max_length=100)
    file_path: str | None = Field(default=None, min_length=1, max_length=500)
    status: str | None = Field(default=None, min_length=1, max_length=50)


class DocumentRead(DocumentBase):
    id: PydanticObjectId
    user_id: PydanticObjectId | None = None
    status: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentList(BaseModel):
    documents: list[DocumentRead] = Field(default_factory=list)


class DocumentStatusRead(BaseModel):
    id: PydanticObjectId
    status: str

    model_config = ConfigDict(from_attributes=True)
