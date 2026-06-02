from __future__ import annotations

import re
import shutil
import subprocess
import textwrap
from html import escape
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field

from app.core.config import settings
from app.utils.files import PROJECT_ROOT, ensure_directory, write_text_file


class PreviewScene(BaseModel):
    scene_id: str
    scene_type: str
    title: str
    visual_description: str
    narration_text: str
    caption_text: str
    duration_seconds: float = Field(default=8.0, ge=0)


class PreviewAssets(BaseModel):
    video_path: str
    preview_path: str
    transcript_path: str


class PreviewPackage(BaseModel):
    title: str
    subject: str
    input_type: str
    source_summary: str
    key_concepts: list[str] = Field(default_factory=list)
    formulas: list[str] = Field(default_factory=list)
    confidence: int = Field(default=65, ge=0, le=100)
    label: str
    scenes: list[PreviewScene] = Field(default_factory=list)
    narration_script: str


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _sentence_chunks(source_text: str, limit: int = 3) -> list[str]:
    sentences = [
        sentence.strip(" .")
        for sentence in re.split(r"(?<=[.!?])\s+", source_text)
        if sentence.strip(" .")
    ]
    if sentences:
        return sentences[:limit]

    words = source_text.split()
    if not words:
        return []

    chunk_size = max(8, len(words) // limit)
    return [
        " ".join(words[index : index + chunk_size])
        for index in range(0, len(words), chunk_size)
    ][:limit]


def _extract_formulas(source_text: str) -> list[str]:
    formulas = re.findall(r"\b[A-Za-z][A-Za-z0-9_ ]{0,12}\s*=\s*[^.;,\n]+", source_text)
    return [_clean_text(formula) for formula in formulas[:3]]


def _extract_key_concepts(source_text: str, subject: str) -> list[str]:
    stop_words = {
        "about",
        "after",
        "also",
        "and",
        "are",
        "because",
        "between",
        "from",
        "has",
        "into",
        "that",
        "the",
        "their",
        "then",
        "this",
        "use",
        "uses",
        "when",
        "with",
    }
    words = re.findall(r"[A-Za-z][A-Za-z-]{3,}", source_text)
    concepts: list[str] = []

    for word in words:
        normalized = word.lower()
        if normalized in stop_words or normalized in [item.lower() for item in concepts]:
            continue
        concepts.append(word)
        if len(concepts) == 4:
            break

    if concepts:
        return concepts

    return [subject]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:60] or "visual-lesson"


def _relative_path(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def _bgr(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return blue, green, red


NAVY = _bgr("#102338")
INK = _bgr("#172033")
MUTED = _bgr("#526070")
BLUE = _bgr("#2364aa")
GREEN = _bgr("#2f8f5b")
GOLD = _bgr("#f2b35d")
LINE = _bgr("#d7e1e8")
SURFACE = _bgr("#ffffff")
BACKGROUND = _bgr("#f4f9fc")
SURFACE_SOFT = _bgr("#f8fbff")
GREEN_SOFT = _bgr("#edf8f2")
GREEN_LINE = _bgr("#b7dec5")
GOLD_DARK = _bgr("#8d621a")


def _put_wrapped_text(
    image: object,
    text: str,
    *,
    x: int,
    y: int,
    max_chars: int,
    font_scale: float,
    color: tuple[int, int, int],
    thickness: int = 1,
    line_height: int = 30,
) -> None:
    import cv2

    for line_index, line in enumerate(textwrap.wrap(text, width=max_chars)[:5]):
        cv2.putText(
            image,
            line,
            (x, y + line_index * line_height),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA,
        )


def _draw_text_block(
    image: object,
    text: str,
    *,
    x: int,
    y: int,
    width_chars: int,
    font_scale: float,
    color: tuple[int, int, int],
    thickness: int = 2,
    line_height: int = 34,
    max_lines: int = 4,
) -> int:
    import cv2

    lines = textwrap.wrap(text, width=width_chars)[:max_lines]
    for line_index, line in enumerate(lines):
        cv2.putText(
            image,
            line,
            (x, y + line_index * line_height),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA,
        )

    return y + max(0, len(lines) - 1) * line_height


def _draw_stem_visual(image: object, subject: str, scene_index: int) -> None:
    import cv2

    subject_key = subject.lower()
    center_x = 980
    center_y = 360

    if "chem" in subject_key:
        colors = [GOLD, GREEN, BLUE]
        points = [(center_x - 105, center_y), (center_x, center_y - 72), (center_x + 105, center_y)]
        for index, point in enumerate(points):
            cv2.circle(image, point, 42, colors[index], -1)
            cv2.circle(image, point, 42, INK, 3)
        cv2.line(image, points[0], points[1], MUTED, 5)
        cv2.line(image, points[1], points[2], MUTED, 5)
        cv2.putText(
            image,
            "Matter",
            (center_x - 74, center_y + 112),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            INK,
            2,
            cv2.LINE_AA,
        )
        return

    if "bio" in subject_key:
        cv2.ellipse(image, (center_x, center_y), (130, 82), 0, 0, 360, GREEN, -1)
        cv2.line(
            image,
            (center_x - 120, center_y + 20),
            (center_x + 110, center_y - 34),
            INK,
            4,
        )
        cv2.circle(image, (center_x, center_y), 32, SURFACE_SOFT, -1)
        cv2.putText(
            image,
            "Life system",
            (center_x - 96, center_y + 132),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            INK,
            2,
            cv2.LINE_AA,
        )
        return

    if "math" in subject_key:
        cv2.line(
            image,
            (center_x - 145, center_y + 96),
            (center_x + 145, center_y + 96),
            MUTED,
            4,
        )
        cv2.line(
            image,
            (center_x - 128, center_y + 120),
            (center_x - 128, center_y - 125),
            MUTED,
            4,
        )
        for offset in range(-120, 121, 24):
            y = center_y + 88 - int((offset / 42) ** 2 * 18)
            cv2.circle(image, (center_x + offset, y), 5, BLUE, -1)
        cv2.putText(
            image,
            "Pattern",
            (center_x - 72, center_y + 148),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            INK,
            2,
            cv2.LINE_AA,
        )
        return

    if "computer" in subject_key or "code" in subject_key:
        for index, label in enumerate(["Input", "Logic", "Output"]):
            x = center_x - 174 + index * 132
            cv2.rectangle(image, (x, center_y - 42), (x + 104, center_y + 42), GREEN_SOFT, -1)
            cv2.rectangle(image, (x, center_y - 42), (x + 104, center_y + 42), GREEN, 3)
            cv2.putText(
                image,
                label,
                (x + 14, center_y + 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                INK,
                2,
                cv2.LINE_AA,
            )
        cv2.line(image, (center_x - 70, center_y), (center_x - 34, center_y), MUTED, 4)
        cv2.line(image, (center_x + 62, center_y), (center_x + 96, center_y), MUTED, 4)
        return

    cv2.arrowedLine(
        image,
        (center_x - 160, center_y + 60),
        (center_x + 150, center_y - 70),
        BLUE,
        8,
        tipLength=0.12,
    )
    cv2.rectangle(
        image,
        (center_x - 75, center_y + 8),
        (center_x + 75, center_y + 96),
        GOLD,
        -1,
    )
    cv2.putText(
        image,
        f"Step {scene_index + 1}",
        (center_x - 72, center_y + 148),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        INK,
        2,
        cv2.LINE_AA,
    )


def _draw_frame(
    package: PreviewPackage,
    scene: PreviewScene,
    *,
    scene_index: int,
    frame_index: int,
    frame_count: int,
    width: int,
    height: int,
) -> object:
    import cv2
    import numpy as np

    frame = np.full((height, width, 3), BACKGROUND, dtype=np.uint8)
    cv2.rectangle(frame, (0, 0), (width, 108), NAVY, -1)
    cv2.rectangle(frame, (0, 108), (width, 116), GOLD, -1)

    _draw_text_block(
        frame,
        package.title,
        x=40,
        y=48,
        width_chars=58,
        font_scale=0.9,
        color=SURFACE,
        line_height=34,
        max_lines=2,
    )
    cv2.putText(
        frame,
        package.subject,
        (1020, 62),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        GOLD,
        2,
        cv2.LINE_AA,
    )

    cv2.rectangle(frame, (54, 154), (808, 622), SURFACE, -1)
    cv2.rectangle(frame, (54, 154), (808, 622), LINE, 2)
    cv2.rectangle(frame, (874, 154), (1218, 622), SURFACE_SOFT, -1)
    cv2.rectangle(frame, (874, 154), (1218, 622), LINE, 2)

    cv2.circle(frame, (112, 226), 38, GREEN, -1)
    cv2.putText(
        frame,
        scene.scene_id,
        (89, 238),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.82,
        SURFACE,
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        scene.scene_type,
        (166, 214),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        BLUE,
        2,
        cv2.LINE_AA,
    )
    _draw_text_block(
        frame,
        scene.title,
        x=166,
        y=256,
        width_chars=34,
        font_scale=0.92,
        color=INK,
        line_height=40,
        max_lines=2,
    )
    _draw_text_block(
        frame,
        scene.narration_text,
        x=86,
        y=370,
        width_chars=54,
        font_scale=0.72,
        color=INK,
        thickness=2,
        line_height=36,
        max_lines=5,
    )

    cv2.putText(
        frame,
        "Visual model",
        (926, 214),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.66,
        BLUE,
        2,
        cv2.LINE_AA,
    )
    _draw_stem_visual(frame, package.subject, scene_index)

    y = 654
    cv2.putText(
        frame,
        "Key concepts:",
        (54, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        MUTED,
        2,
        cv2.LINE_AA,
    )
    x = 210
    for concept in package.key_concepts[:4]:
        chip_width = min(210, 38 + len(concept) * 13)
        cv2.rectangle(frame, (x, y - 28), (x + chip_width, y + 12), GREEN_SOFT, -1)
        cv2.rectangle(frame, (x, y - 28), (x + chip_width, y + 12), GREEN_LINE, 2)
        cv2.putText(
            frame,
            concept[:16],
            (x + 14, y - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            GREEN,
            2,
            cv2.LINE_AA,
        )
        x += chip_width + 14

    progress = frame_index / max(1, frame_count - 1)
    cv2.rectangle(frame, (0, height - 8), (width, height), LINE, -1)
    cv2.rectangle(frame, (0, height - 8), (int(width * progress), height), BLUE, -1)
    return frame


def _transcode_for_browser(source_path: Path, output_path: Path) -> None:
    if not shutil.which("ffmpeg"):
        source_path.replace(output_path)
        return

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True)
    source_path.unlink(missing_ok=True)


def _write_mp4(package: PreviewPackage, output_path: Path) -> Path:
    import cv2

    width = 1280
    height = 720
    fps = 12
    raw_path = output_path.with_name(f"{output_path.stem}-raw.mp4")
    writer = cv2.VideoWriter(
        str(raw_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    if not writer.isOpened():
        raise RuntimeError("OpenCV could not create the MP4 preview file.")

    try:
        for scene_index, scene in enumerate(package.scenes):
            frame_count = max(1, int(fps * scene.duration_seconds))
            for frame_index in range(frame_count):
                frame = _draw_frame(
                    package,
                    scene,
                    scene_index=scene_index,
                    frame_index=frame_index,
                    frame_count=frame_count,
                    width=width,
                    height=height,
                )
                writer.write(frame)
    finally:
        writer.release()

    _transcode_for_browser(raw_path, output_path)
    return output_path


def build_preview_package(
    *,
    title: str,
    subject: str,
    input_type: str,
    source_text: str,
) -> PreviewPackage:
    cleaned_text = _clean_text(source_text)

    if not cleaned_text:
        raise ValueError("Notes or uploaded file text is required to create a video preview.")

    cleaned_title = _clean_text(title) or _sentence_chunks(cleaned_text, 1)[0][:80]
    concepts = _extract_key_concepts(cleaned_text, subject)
    formulas = _extract_formulas(cleaned_text)
    chunks = _sentence_chunks(cleaned_text, 3)
    summary = chunks[0] if chunks else cleaned_text[:160]
    confidence = min(96, max(58, len(cleaned_text.split()) * 4))
    label = formulas[0] if formulas else concepts[0][:12]

    scene_inputs = [
        (
            "01",
            "Concept intro",
            f"Introduce {concepts[0]}",
            chunks[0] if len(chunks) > 0 else summary,
        ),
        (
            "02",
            "Visual explanation",
            "Build a clear visual model",
            chunks[1] if len(chunks) > 1 else summary,
        ),
        (
            "03",
            "Quick recap",
            "Review the key idea",
            chunks[2] if len(chunks) > 2 else summary,
        ),
    ]

    scenes = [
        PreviewScene(
            scene_id=scene_id,
            scene_type=scene_type,
            title=scene_title,
            visual_description=(
                f"Show a {subject.lower()} visual using simple labels, arrows, "
                "and highlighted keywords."
            ),
            narration_text=narration,
            caption_text=narration,
            duration_seconds=8.0,
        )
        for scene_id, scene_type, scene_title, narration in scene_inputs
    ]

    narration_script = " ".join(scene.narration_text for scene in scenes)

    return PreviewPackage(
        title=cleaned_title,
        subject=subject,
        input_type=input_type,
        source_summary=summary,
        key_concepts=concepts,
        formulas=formulas,
        confidence=confidence,
        label=label,
        scenes=scenes,
        narration_script=narration_script,
    )


def write_preview_assets(
    package: PreviewPackage,
    output_directory: str | Path | None = None,
) -> PreviewAssets:
    directory = ensure_directory(output_directory or settings.videos_dir)
    file_stem = f"{_slugify(package.title)}-{uuid4().hex[:8]}"
    video_path = directory / f"{file_stem}.mp4"
    preview_path = directory / f"{file_stem}.html"
    transcript_path = directory / f"{file_stem}-transcript.txt"
    video_filename = escape(video_path.name)
    scene_items = "\n".join(
        f"""
        <article class="scene">
          <span>{escape(scene.scene_id)}</span>
          <h2>{escape(scene.title)}</h2>
          <p>{escape(scene.narration_text)}</p>
        </article>
        """
        for scene in package.scenes
    )
    concept_items = "".join(f"<li>{escape(concept)}</li>" for concept in package.key_concepts)
    formula_items = "".join(f"<li>{escape(formula)}</li>" for formula in package.formulas)
    formulas_block = (
        f"<ul>{formula_items}</ul>" if package.formulas else "<p>No formula detected.</p>"
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escape(package.title)} preview</title>
    <style>
      body {{
        margin: 0;
        min-height: 100vh;
        background: #102338;
        color: #f8fbff;
        font-family: Arial, sans-serif;
      }}
      main {{
        max-width: 960px;
        margin: 0 auto;
        padding: 36px;
      }}
      .stage {{
        min-height: 360px;
        padding: 28px;
        border-radius: 8px;
        background: #f8fbff;
        color: #172033;
      }}
      video {{
        display: block;
        width: 100%;
        margin: 22px 0;
        border-radius: 8px;
        background: #000;
      }}
      .scene {{
        padding: 18px 0;
        border-bottom: 1px solid #d7e1e8;
      }}
      .scene span {{
        color: #2364aa;
        font-weight: 800;
      }}
      h1 {{
        margin-top: 0;
      }}
      ul {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        padding: 0;
        list-style: none;
      }}
      li {{
        padding: 8px 10px;
        border-radius: 8px;
        background: #edf8f2;
        color: #1d6a43;
        font-weight: 700;
      }}
    </style>
  </head>
  <body>
    <main>
      <p>{escape(package.subject)} visual lesson preview</p>
      <section class="stage">
        <h1>{escape(package.title)}</h1>
        <p>{escape(package.source_summary)}</p>
        <video src="{video_filename}" controls preload="metadata"></video>
        <h2>Key concepts</h2>
        <ul>{concept_items}</ul>
        <h2>Formulas</h2>
        {formulas_block}
        <h2>Storyboard scenes</h2>
        {scene_items}
      </section>
    </main>
  </body>
</html>
"""
    transcript = "\n\n".join(
        [package.title, package.source_summary, *[scene.narration_text for scene in package.scenes]]
    )

    written_video_path = _write_mp4(package, video_path)
    written_preview_path = write_text_file(preview_path, html)
    written_transcript_path = write_text_file(transcript_path, transcript)

    return PreviewAssets(
        video_path=_relative_path(written_video_path),
        preview_path=_relative_path(written_preview_path),
        transcript_path=_relative_path(written_transcript_path),
    )
