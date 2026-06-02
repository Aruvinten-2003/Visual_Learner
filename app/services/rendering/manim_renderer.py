from dataclasses import dataclass
from pathlib import Path

from app.schemas.storyboard import SceneBase
from app.utils.files import ensure_directory, write_text_file


@dataclass(slots=True)
class RenderedScene:
    scene_id: str
    script_path: Path
    video_path: Path | None = None
    duration_seconds: float = 0.0


class ManimRenderer:
    def create_scene_script(self, scene: SceneBase, output_dir: str | Path) -> Path:
        directory = ensure_directory(output_dir)
        class_name = self._scene_class_name(scene.scene_id)
        script = self.build_scene_script(scene, class_name)
        return write_text_file(directory / f"{scene.scene_id}.py", script)

    def build_scene_script(self, scene: SceneBase, class_name: str | None = None) -> str:
        safe_title = scene.title.replace('"', '\\"')
        safe_description = scene.visual_description.replace('"', '\\"')
        class_name = class_name or self._scene_class_name(scene.scene_id)

        return f'''from manim import *


class {class_name}(Scene):
    def construct(self):
        title = Text("{safe_title}", font_size=42)
        subtitle = Text("{safe_description}", font_size=26).next_to(title, DOWN)
        self.play(Write(title))
        if "{safe_description}":
            self.play(FadeIn(subtitle))
        self.wait(1)
'''

    def prepare_scene(self, scene: SceneBase, output_dir: str | Path) -> RenderedScene:
        script_path = self.create_scene_script(scene, output_dir)
        return RenderedScene(
            scene_id=scene.scene_id,
            script_path=script_path,
            duration_seconds=scene.duration_seconds,
        )

    @staticmethod
    def _scene_class_name(scene_id: str) -> str:
        parts = "".join(char if char.isalnum() else " " for char in scene_id).title().split()
        return f"{''.join(parts) or 'Generated'}Scene"
