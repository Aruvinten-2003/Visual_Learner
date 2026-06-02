from dataclasses import dataclass, field
from pathlib import Path

from app.utils.files import ensure_parent_dir, resolve_project_path


@dataclass(slots=True)
class VideoAssemblyPlan:
    scene_paths: list[Path] = field(default_factory=list)
    audio_path: Path | None = None
    captions_path: Path | None = None
    output_path: Path | None = None


class VideoAssembler:
    def write_webvtt(self, segments: list[dict[str, float | str]], output_path: str | Path) -> Path:
        resolved = resolve_project_path(output_path)
        ensure_parent_dir(resolved)
        lines = ["WEBVTT", ""]

        for segment in segments:
            start = self._format_timestamp(float(segment["start_seconds"]))
            end = self._format_timestamp(float(segment["end_seconds"]))
            text = str(segment["text"])
            lines.extend([f"{start} --> {end}", text, ""])

        resolved.write_text("\n".join(lines), encoding="utf-8")
        return resolved

    def create_assembly_plan(
        self,
        scene_paths: list[str | Path],
        output_path: str | Path,
        audio_path: str | Path | None = None,
        captions_path: str | Path | None = None,
    ) -> VideoAssemblyPlan:
        return VideoAssemblyPlan(
            scene_paths=[resolve_project_path(path) for path in scene_paths],
            audio_path=resolve_project_path(audio_path) if audio_path else None,
            captions_path=resolve_project_path(captions_path) if captions_path else None,
            output_path=resolve_project_path(output_path),
        )

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        milliseconds = int(round((seconds - int(seconds)) * 1000))
        total_seconds = int(seconds)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"
