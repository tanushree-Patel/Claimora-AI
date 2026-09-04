import io

import pypdf
import pytest

from app.services.document_ingestion_service import DocumentIngestionService
from app.services.exceptions import ExtractionError


def _make_native_text_pdf(text: str) -> bytes:
    # Minimal helper: reportlab or a fixture PDF is more realistic;
    # for this test, use a pre-generated fixture file under tests/fixtures/
    with open("tests/fixtures/native_text_sample.pdf", "rb") as f:
        return f.read()


def test_native_extraction_used_when_text_present():
    service = DocumentIngestionService()
    pdf_bytes = _make_native_text_pdf("Patient Asha Rao, essential hypertension.")
    text = service.extract_text(pdf_bytes)
    assert "hypertension" in text.lower()


def test_ocr_fallback_on_scanned_pdf():
    service = DocumentIngestionService()
    with open("tests/fixtures/scanned_sample.pdf", "rb") as f:
        pdf_bytes = f.read()
    text = service.extract_text(pdf_bytes)
    assert len(text.strip()) > 0


def test_unreadable_document_raises():
    service = DocumentIngestionService()
    with open("tests/fixtures/blank_sample.pdf", "rb") as f:
        pdf_bytes = f.read()
    with pytest.raises(ExtractionError):
        service.extract_text(pdf_bytes)