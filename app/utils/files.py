from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)

    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate

    resolved = candidate.resolve()

    if resolved != PROJECT_ROOT and PROJECT_ROOT not in resolved.parents:
        raise ValueError(f"Path is outside the project root: {resolved}")

    return resolved


def ensure_directory(path: str | Path) -> Path:
    resolved = resolve_project_path(path)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def ensure_parent_dir(path: str | Path) -> Path:
    resolved = resolve_project_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved.parent


def write_text_file(path: str | Path, content: str) -> Path:
    resolved = resolve_project_path(path)
    ensure_parent_dir(resolved)
    resolved.write_text(content, encoding="utf-8")
    return resolved


def read_text_file(path: str | Path) -> str:
    return resolve_project_path(path).read_text(encoding="utf-8")
