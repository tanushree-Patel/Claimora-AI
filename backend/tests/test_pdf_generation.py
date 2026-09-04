from app.services.pdf_generation_service import PdfGenerationService


def test_generate_creates_pdf_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    service = PdfGenerationService()
    path = service.generate(
        extracted_data={
            "patient": {"full_name": "Asha Rao"},
            "hospital": {"hospital_name": "Apollo"},
            "clinical": {"diagnosis_text": "hypertension"},
        },
        verified_codes={"approved_codes": ["I10"], "notes": "Confirmed"},
        session_id="test-session",
    )
    assert (tmp_path / path).exists()