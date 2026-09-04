import io

import pypdf
import pytesseract
from pdf2image import convert_from_bytes

from app.core.logging import get_logger
from app.services.exceptions import ExtractionError

logger = get_logger(__name__)

MIN_NATIVE_TEXT_CHARS = 40  # below this, assume the PDF is scanned/image-only


class DocumentIngestionService:
    def extract_text(self, file_bytes: bytes) -> str:
        native_text = self._try_native_extraction(file_bytes)
        if len(native_text.strip()) >= MIN_NATIVE_TEXT_CHARS:
            logger.info("Using native PDF text extraction (%d chars)", len(native_text))
            return native_text

        logger.info("Native extraction insufficient, falling back to OCR")
        return self._ocr_extraction(file_bytes)

    def _try_native_extraction(self, file_bytes: bytes) -> str:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            logger.warning("Native PDF extraction failed: %s", exc)
            return ""

    def _ocr_extraction(self, file_bytes: bytes) -> str:
        try:
            images = convert_from_bytes(file_bytes)
            text_parts = [pytesseract.image_to_string(img) for img in images]
            text = "\n".join(text_parts)
        except Exception as exc:
            logger.error("OCR extraction failed: %s", exc)
            raise ExtractionError("Could not extract text from document via OCR") from exc

        if len(text.strip()) < MIN_NATIVE_TEXT_CHARS:
            raise ExtractionError("Document appears to contain no readable text")
        return text