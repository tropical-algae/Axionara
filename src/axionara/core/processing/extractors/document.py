import io
from dataclasses import dataclass
from pathlib import Path

from markitdown import MarkItDown


@dataclass(frozen=True)
class DocumentExtractionResult:
    text: str
    status: str
    engine: str
    error_message: str | None = None
    truncated: bool = False

    @property
    def text_chars(self) -> int:
        return len(self.text)


class DocumentTextExtractor:
    def __init__(self, max_chars: int = 20000):
        self.max_chars = max_chars

    def extract(self, filename: str, content: bytes) -> DocumentExtractionResult:
        extension = Path(filename).suffix.lower()
        if not content:
            return DocumentExtractionResult(
                text="",
                status="skipped",
                engine="markitdown",
                error_message="empty_content",
            )
        try:
            converter = MarkItDown(enable_plugins=False)
            result = converter.convert_stream(
                io.BytesIO(content),
                file_extension=extension,
            )
            text = (result.text_content or "").strip()
            truncated = len(text) > self.max_chars
            if truncated:
                text = text[: self.max_chars]
            return DocumentExtractionResult(
                text=text,
                status="completed" if text else "skipped",
                engine="markitdown",
                error_message=None if text else "no_extractable_text",
                truncated=truncated,
            )
        except Exception as err:
            return DocumentExtractionResult(
                text="",
                status="failed",
                engine="markitdown",
                error_message=str(err),
            )
