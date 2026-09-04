from unittest.mock import MagicMock, patch

import pytest

from app.services.document_ingestion_service import DocumentIngestionService
from app.services.exceptions import ExtractionError


def test_native_extraction_used_when_text_present():
    service = DocumentIngestionService()
    fake_text = "Patient Asha Rao, essential hypertension diagnosed at Apollo Hospital."

    mock_page = MagicMock()
    mock_page.extract_text.return_value = fake_text
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    with patch("pypdf.PdfReader", return_value=mock_reader):
        text = service.extract_text(b"%PDF-fake")
    assert "hypertension" in text.lower()


def test_ocr_fallback_on_scanned_pdf():
    service = DocumentIngestionService()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    with patch("pypdf.PdfReader", return_value=mock_reader), patch(
        "app.services.document_ingestion_service.convert_from_bytes", return_value=[MagicMock()]
    ), patch(
        "app.services.document_ingestion_service.pytesseract.image_to_string",
        return_value="Patient Asha Rao, essential hypertension diagnosed at Apollo Hospital.",
    ):
        text = service.extract_text(b"%PDF-fake")
    assert len(text.strip()) > 0


def test_unreadable_document_raises():
    service = DocumentIngestionService()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    with patch("pypdf.PdfReader", return_value=mock_reader), patch(
        "app.services.document_ingestion_service.convert_from_bytes", return_value=[MagicMock()]
    ), patch("app.services.document_ingestion_service.pytesseract.image_to_string", return_value=""):
        with pytest.raises(ExtractionError):
            service.extract_text(b"%PDF-fake")