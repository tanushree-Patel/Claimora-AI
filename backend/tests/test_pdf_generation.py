import pytest

from app.services.exceptions import ExtractionError
from app.services.pdf_generation_service import PdfGenerationService


def test_generate_creates_pdf_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "irdai_part_b_template.pdf").touch()

    service = PdfGenerationService()
    path = service.generate(
        extracted_data={"patient": {"full_name": "Asha Rao"}, "hospital": {"hospital_name": "Apollo"}, "clinical": {"diagnosis_text": "hypertension"}},
        verified_codes={"approved_codes": ["I10"], "notes": "Confirmed"},
        session_id="test-session",
    )
    assert (tmp_path / path).exists()


def test_generate_raises_when_template_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    service = PdfGenerationService()
    with pytest.raises(ExtractionError):
        service.generate(extracted_data={}, verified_codes={}, session_id="missing-template")