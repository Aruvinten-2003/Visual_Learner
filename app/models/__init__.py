from app.models.accessibility_preference import AccessibilityPreference
from app.models.document import LearningDocument
from app.models.extracted_content import ExtractedContent
from app.models.lesson_plan import LessonPlan
from app.models.media_asset import MediaAsset
from app.models.render_job import RenderJob
from app.models.storyboard import Scene, Storyboard
from app.models.user import User
from app.models.video import Video

DOCUMENT_MODELS = [
    User,
    AccessibilityPreference,
    LearningDocument,
    ExtractedContent,
    LessonPlan,
    Storyboard,
    RenderJob,
    MediaAsset,
    Video,
]

__all__ = [
    "AccessibilityPreference",
    "DOCUMENT_MODELS",
    "ExtractedContent",
    "LearningDocument",
    "LessonPlan",
    "MediaAsset",
    "RenderJob",
    "Scene",
    "Storyboard",
    "User",
    "Video",
]
