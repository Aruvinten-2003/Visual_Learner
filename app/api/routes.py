import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.database import get_database_status, ping_database
from app.models import LearningDocument, LessonPlan, RenderJob, Scene, Storyboard, Video
from app.services.ocr.extractor import OCRExtractor
from app.services.video.preview_generator import (
    PreviewAssets,
    PreviewPackage,
    build_preview_package,
    write_preview_assets,
)
from app.utils.files import PROJECT_ROOT, ensure_directory

router = APIRouter()


def _safe_file_name(filename: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "-", filename.strip()).strip(".-")
    return cleaned[:120] or "uploaded-source"


def _relative_path(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def _decode_text_upload(file_bytes: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in {".txt", ".md", ".csv"}:
        return ""

    return file_bytes.decode("utf-8", errors="ignore").strip()


async def _save_upload(file: UploadFile | None) -> tuple[str | None, str]:
    if file is None or not file.filename:
        return None, ""

    file_bytes = await file.read()
    safe_name = _safe_file_name(file.filename)
    upload_path = ensure_directory(settings.uploads_dir) / f"{uuid4().hex}-{safe_name}"
    upload_path.write_bytes(file_bytes)
    relative_upload_path = _relative_path(upload_path)
    extracted_text = _decode_text_upload(file_bytes, safe_name)

    if not extracted_text:
        try:
            extracted_text = OCRExtractor().extract_text(relative_upload_path).text
        except Exception:
            extracted_text = ""

    return relative_upload_path, extracted_text


async def _persist_preview(
    package: PreviewPackage,
    assets: PreviewAssets,
    upload_path: str | None,
) -> dict[str, str | bool | None]:
    if not get_database_status()["ready"]:
        return {"persisted": False}

    now = datetime.now(UTC)

    try:
        document = LearningDocument(
            title=package.title,
            input_type=package.input_type,
            subject=package.subject,
            file_path=upload_path,
            status="preview_created",
        )
        await document.insert()

        lesson = LessonPlan(
            document_id=document.id,
            title=package.title,
            subject=package.subject,
            difficulty_level="beginner",
            key_concepts=package.key_concepts,
            formulas=package.formulas,
            simplified_explanation=package.source_summary,
        )
        await lesson.insert()

        storyboard = Storyboard(
            lesson_plan_id=lesson.id,
            scenes=[
                Scene(
                    scene_id=scene.scene_id,
                    scene_type=scene.scene_type,
                    title=scene.title,
                    visual_description=scene.visual_description,
                    narration_text=scene.narration_text,
                    caption_text=scene.caption_text,
                    duration_seconds=scene.duration_seconds,
                )
                for scene in package.scenes
            ],
            narration_script=package.narration_script,
            status="preview_created",
        )
        await storyboard.insert()

        render_job = RenderJob(
            storyboard_id=storyboard.id,
            job_status="completed",
            progress=100,
            started_at=now,
            completed_at=now,
        )
        await render_job.insert()

        video = Video(
            document_id=document.id,
            render_job_id=render_job.id,
            title=package.title,
            video_path=assets.video_path,
            transcript_path=assets.transcript_path,
            duration_seconds=sum(scene.duration_seconds for scene in package.scenes),
        )
        await video.insert()
    except Exception:
        return {"persisted": False}

    return {
        "persisted": True,
        "document_id": str(document.id),
        "lesson_plan_id": str(lesson.id),
        "storyboard_id": str(storyboard.id),
        "render_job_id": str(render_job.id),
        "video_id": str(video.id),
    }


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Visual Learner API"}


@router.get("/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
        "mongodb": get_database_status(),
    }


@router.get("/health/mongodb")
async def mongodb_health() -> dict[str, str | bool]:
    return await ping_database()


@router.post("/videos/preview", status_code=status.HTTP_201_CREATED)
async def create_video_preview(
    title: Annotated[str, Form(min_length=2, max_length=255)],
    subject: Annotated[str, Form(min_length=2, max_length=100)],
    input_type: Annotated[str, Form(min_length=1, max_length=50)],
    notes: Annotated[str, Form()] = "",
    file: Annotated[UploadFile | None, File()] = None,
) -> dict[str, object]:
    upload_path, uploaded_text = await _save_upload(file)
    source_text = notes.strip() or uploaded_text.strip()

    if not source_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Add notes or upload a text-readable file. PDF/image OCR can fail "
                "if the file is scanned, unclear, or Tesseract is not available."
            ),
        )

    try:
        package = build_preview_package(
            title=title,
            subject=subject,
            input_type=input_type,
            source_text=source_text,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    assets = write_preview_assets(package)
    persistence = await _persist_preview(package, assets, upload_path)

    return {
        "status": "preview_created",
        "message": "Preview MP4 created. Full Manim/TTS rendering is the next pipeline step.",
        "persisted": persistence.get("persisted", False),
        "ids": persistence,
        "project": {
            "title": package.title,
            "subject": package.subject,
            "input_type": package.input_type,
            "source": upload_path or "typed notes",
            "scenes": len(package.scenes),
        },
        "lesson": {
            "title": package.title,
            "subject": package.subject,
            "summary": package.source_summary,
            "key_concepts": package.key_concepts,
            "formulas": package.formulas,
            "confidence": package.confidence,
        },
        "storyboard": {
            "title": package.title,
            "confidence": package.confidence,
            "scenes": [scene.model_dump() for scene in package.scenes],
            "narration_script": package.narration_script,
        },
        "render_job": {
            "title": package.title,
            "step": "Preview package created",
            "progress": 100,
            "status": "completed",
        },
        "video": {
            "title": package.title,
            "video_path": assets.video_path,
            "preview_path": assets.preview_path,
            "transcript_path": assets.transcript_path,
            "duration_seconds": sum(scene.duration_seconds for scene in package.scenes),
            "label": package.label,
            "description": "MP4 preview - full renderer pending",
        },
    }
