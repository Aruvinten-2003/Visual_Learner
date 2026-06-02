from datetime import UTC, datetime

from beanie import Document
from pydantic import Field


class User(Document):
    name: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "users"
