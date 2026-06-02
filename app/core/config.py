from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Visual Learner API"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", validation_alias="OPENAI_MODEL")
    tts_model: str = Field(default="tts-1", validation_alias="TTS_MODEL")
    tts_voice: str = Field(default="alloy", validation_alias="TTS_VOICE")

    mongodb_uri: str = Field(default="mongodb://localhost:27017", validation_alias="MONGODB_URI")
    mongodb_database: str = Field(default="visual_learner", validation_alias="MONGODB_DATABASE")
    mongodb_timeout_ms: int = 3000
    database_required: bool = False

    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1",
        validation_alias="CELERY_RESULT_BACKEND",
    )

    assets_dir: str = Field(default="assets", validation_alias="ASSETS_DIR")
    uploads_dir: str = Field(default="assets/temp", validation_alias="UPLOADS_DIR")
    videos_dir: str = Field(default="assets/videos", validation_alias="VIDEOS_DIR")
    audio_dir: str = Field(default="assets/audio", validation_alias="AUDIO_DIR")
    images_dir: str = Field(default="assets/images", validation_alias="IMAGES_DIR")
    tesseract_cmd: str = Field(default="", validation_alias="TESSERACT_CMD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def mongodb_uri_has_placeholders(self) -> bool:
        placeholder_parts = ("<username>", "<password>", "xxxxx", "your_")
        return any(part in self.mongodb_uri for part in placeholder_parts)

    @property
    def openai_api_key_is_placeholder(self) -> bool:
        if not self.openai_api_key:
            return True

        placeholder_parts = ("your_", "sk-your", "replace_me", "<")
        return any(self.openai_api_key.startswith(part) for part in placeholder_parts)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
