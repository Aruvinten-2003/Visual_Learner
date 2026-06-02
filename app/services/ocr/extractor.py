from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import fitz
import pdfplumber
import pytesseract
from PIL import Image

from app.core.config import settings
from app.utils.files import resolve_project_path


@dataclass(slots=True)
class OCRResult:
    text: str
    source_type: str
    confidence_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class OCRExtractor:
    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}

    def __init__(self) -> None:
        if settings.tesseract_cmd:
            tesseract_path = Path(settings.tesseract_cmd)
            if tesseract_path.exists():
                pytesseract.pytesseract.tesseract_cmd = str(tesseract_path)

    def clean_text(self, text: str) -> str:
        return " ".join(text.split()).strip()

    def extract_text(self, file_path: str | Path) -> OCRResult:
        resolved = resolve_project_path(file_path)
        suffix = resolved.suffix.lower()

        if suffix == ".pdf":
            return self.extract_from_pdf(resolved)

        if suffix in self.image_extensions:
            return self.extract_from_image(resolved)

        if suffix in {".txt", ".md"}:
            return OCRResult(
                text=self.clean_text(resolved.read_text(encoding="utf-8")),
                source_type="text",
                confidence_score=1.0,
                metadata={"path": str(resolved)},
            )

        raise ValueError(f"Unsupported file type for OCR extraction: {suffix}")

    def extract_from_pdf(self, file_path: str | Path) -> OCRResult:
        resolved = resolve_project_path(file_path)
        pages: list[str] = []

        with fitz.open(resolved) as document:
            for page in document:
                pages.append(page.get_text())

        text = self.clean_text("\n".join(pages))

        if not text:
            with pdfplumber.open(resolved) as pdf:
                text = self.clean_text("\n".join(page.extract_text() or "" for page in pdf.pages))

        return OCRResult(
            text=text,
            source_type="pdf",
            confidence_score=0.9 if text else 0.0,
            metadata={"path": str(resolved), "pages": len(pages)},
        )

    def extract_from_image(self, file_path: str | Path) -> OCRResult:
        resolved = resolve_project_path(file_path)

        with Image.open(resolved) as image:
            text = pytesseract.image_to_string(image)

        cleaned = self.clean_text(text)
        return OCRResult(
            text=cleaned,
            source_type="image",
            confidence_score=0.75 if cleaned else 0.0,
            metadata={"path": str(resolved)},
        )
