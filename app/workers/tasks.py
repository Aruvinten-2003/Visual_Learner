from typing import Any

from app.workers.celery_app import celery_app


def _queued_payload(task_name: str, resource_id: str, **extra: Any) -> dict[str, Any]:
    return {
        "task": task_name,
        "resource_id": resource_id,
        "status": "queued",
        **extra,
    }


@celery_app.task(name="extract_input_job")
def extract_input_job(document_id: str) -> dict[str, Any]:
    return _queued_payload("extract_input_job", document_id)


@celery_app.task(name="run_lesson_plan_job")
def run_lesson_plan_job(document_id: str) -> dict[str, Any]:
    return _queued_payload("run_lesson_plan_job", document_id)


@celery_app.task(name="render_manim_scenes_job")
def render_manim_scenes_job(storyboard_id: str) -> dict[str, Any]:
    return _queued_payload("render_manim_scenes_job", storyboard_id)


@celery_app.task(name="generate_narration_job")
def generate_narration_job(storyboard_id: str) -> dict[str, Any]:
    return _queued_payload("generate_narration_job", storyboard_id)


@celery_app.task(name="assemble_video_job")
def assemble_video_job(render_job_id: str) -> dict[str, Any]:
    return _queued_payload("assemble_video_job", render_job_id)
