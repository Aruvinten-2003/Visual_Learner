from dataclasses import dataclass
from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import settings
from app.utils.files import ensure_parent_dir, resolve_project_path


@dataclass(slots=True)
class NarrationAsset:
    script: str
    audio_path: Path
    voice: str
    model: str


class TTSService:
    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        self.client = client

    def create_caption_segments(
        self,
        script: str,
        words_per_segment: int = 8,
        seconds_per_segment: float = 3.0,
    ) -> list[dict[str, float | str]]:
        words = script.split()
        segments: list[dict[str, float | str]] = []

        for index in range(0, len(words), words_per_segment):
            segment_index = index // words_per_segment
            text = " ".join(words[index : index + words_per_segment])
            segments.append(
                {
                    "start_seconds": round(segment_index * seconds_per_segment, 2),
                    "end_seconds": round((segment_index + 1) * seconds_per_segment, 2),
                    "text": text,
                }
            )

        return segments

    async def generate_narration(
        self,
        script: str,
        output_path: str | Path,
        voice: str | None = None,
        model: str | None = None,
    ) -> NarrationAsset:
        if not script.strip():
            raise ValueError("script must not be empty")

        resolved = resolve_project_path(output_path)
        ensure_parent_dir(resolved)
        voice = voice or settings.tts_voice
        model = model or settings.tts_model

        if settings.openai_api_key_is_placeholder:
            raise RuntimeError("Set a real OPENAI_API_KEY in .env before generating narration.")

        client = self.client or AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.audio.speech.create(model=model, voice=voice, input=script)
        audio_bytes = await response.aread()
        resolved.write_bytes(audio_bytes)

        return NarrationAsset(script=script, audio_path=resolved, voice=voice, model=model)
