from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.core.logging import get_logger
from app.services.exceptions import ExtractionError

logger = get_logger(__name__)

TEMPLATE_PATH = Path("assets/irdai_part_b_template.pdf")
OUTPUT_DIR = Path("generated_pdfs")


class PdfGenerationService:
    def generate(self, extracted_data: dict, verified_codes: dict, session_id: str) -> str:
        if not TEMPLATE_PATH.exists():
            raise ExtractionError(f"PDF template not found at {TEMPLATE_PATH}")

        patient = extracted_data.get("patient", {})
        hospital = extracted_data.get("hospital", {})
        clinical = extracted_data.get("clinical", {})
        approved_codes = ", ".join(verified_codes.get("approved_codes", []))

        field_values = {
            "patient_name": patient.get("full_name", ""),
            "policy_number": patient.get("policy_number", ""),
            "abha_id": patient.get("abha_id", ""),
            "hospital_name": hospital.get("hospital_name", ""),
            "admission_date": hospital.get("admission_date", ""),
            "discharge_date": hospital.get("discharge_date", ""),
            "diagnosis": clinical.get("diagnosis_text", ""),
            "diagnosis_codes": approved_codes,
            "reviewer_notes": verified_codes.get("notes", ""),
        }

        try:
            reader = PdfReader(str(TEMPLATE_PATH))
            writer = PdfWriter()
            writer.append(reader)
            if reader.get_fields():
                for page in writer.pages:
                    writer.update_page_form_field_values(page, field_values)
        except Exception as exc:
            logger.error("PDF fill failed: %s", exc)
            raise ExtractionError("Failed to generate claim PDF") from exc

        OUTPUT_DIR.mkdir(exist_ok=True)
        output_path = OUTPUT_DIR / f"claim_{session_id}.pdf"
        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info("Generated claim PDF at %s", output_path)
        return str(output_path)