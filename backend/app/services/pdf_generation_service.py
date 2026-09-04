from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.logging import get_logger
from app.services.exceptions import ExtractionError

logger = get_logger(__name__)

OUTPUT_DIR = Path("generated_pdfs")


class PdfGenerationService:
    def generate(self, extracted_data: dict, verified_codes: dict, session_id: str) -> str:
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_path = OUTPUT_DIR / f"claim_{session_id}.pdf"

        patient = extracted_data.get("patient") or {}
        hospital = extracted_data.get("hospital") or {}
        clinical = extracted_data.get("clinical") or {}

        approved_codes_list = verified_codes.get("approved_codes") or []
        approved_codes_str = (
            ", ".join(approved_codes_list) if approved_codes_list else "None specified"
        )
        reviewer_notes = verified_codes.get("notes") or "N/A"

        try:
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36,
            )
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "DocTitle",
                parent=styles["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=16,
                leading=20,
                textColor=colors.HexColor("#0f172a"),
                alignment=1,
            )
            subtitle_style = ParagraphStyle(
                "DocSubTitle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#475569"),
                alignment=1,
            )
            section_title_style = ParagraphStyle(
                "SectionTitle",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                textColor=colors.HexColor("#1e293b"),
                spaceBefore=8,
                spaceAfter=4,
            )
            body_style = ParagraphStyle(
                "BodyCustom",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#334155"),
            )

            story = []

            # Title Header
            story.append(Paragraph("IRDAI CLAIM FORM - PART B", title_style))
            story.append(
                Paragraph(
                    "DETAILS OF HOSPITAL / MEDICAL PRACTITIONER (SUMMARY & CODING)",
                    subtitle_style,
                )
            )
            story.append(Spacer(1, 10))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=2,
                    color=colors.HexColor("#2563eb"),
                    spaceAfter=12,
                )
            )

            # Metadata Table
            meta_data = [
                [
                    Paragraph(f"<b>Claim Session ID:</b> {session_id}", body_style),
                    Paragraph("<b>Status:</b> COMPLETED", body_style),
                ]
            ]
            meta_table = Table(meta_data, colWidths=[360, 180])
            meta_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#bfdbfe")),
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(meta_table)
            story.append(Spacer(1, 12))

            # Section A: Patient & Policy Details
            story.append(Paragraph("SECTION A: PATIENT & POLICY DETAILS", section_title_style))
            patient_grid = [
                [
                    Paragraph(
                        f"<b>Full Name:</b> {patient.get('full_name') or 'N/A'}", body_style
                    ),
                    Paragraph(
                        f"<b>Policy Number:</b> {patient.get('policy_number') or 'N/A'}", body_style
                    ),
                ],
                [
                    Paragraph(f"<b>ABHA ID:</b> {patient.get('abha_id') or 'N/A'}", body_style),
                    Paragraph(
                        f"<b>Age / Gender:</b> {patient.get('age') or 'N/A'} / {patient.get('gender') or 'N/A'}",
                        body_style,
                    ),
                ],
            ]
            t_patient = Table(patient_grid, colWidths=[270, 270])
            t_patient.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(t_patient)
            story.append(Spacer(1, 12))

            # Section B: Hospital Details
            story.append(Paragraph("SECTION B: HOSPITAL DETAILS", section_title_style))
            hosp_grid = [
                [
                    Paragraph(
                        f"<b>Hospital Name:</b> {hospital.get('hospital_name') or 'N/A'}",
                        body_style,
                    ),
                    Paragraph(
                        f"<b>Hospital ID:</b> {hospital.get('hospital_id') or 'N/A'}", body_style
                    ),
                ],
                [
                    Paragraph(
                        f"<b>Admission Date:</b> {hospital.get('admission_date') or 'N/A'}",
                        body_style,
                    ),
                    Paragraph(
                        f"<b>Discharge Date:</b> {hospital.get('discharge_date') or 'N/A'}",
                        body_style,
                    ),
                ],
            ]
            t_hosp = Table(hosp_grid, colWidths=[270, 270])
            t_hosp.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(t_hosp)
            story.append(Spacer(1, 12))

            # Section C: Clinical Details & Approved Medical Coding
            story.append(
                Paragraph(
                    "SECTION C: CLINICAL DIAGNOSIS & APPROVED MEDICAL CODES", section_title_style
                )
            )
            clinical_grid = [
                [
                    Paragraph(
                        f"<b>Clinical Diagnosis Summary:</b><br/>{clinical.get('diagnosis_text') or 'N/A'}",
                        body_style,
                    )
                ],
                [
                    Paragraph(
                        f"<b>Approved ICD-10 / SNOMED-CT Codes:</b><br/><font color='#15803d'><b>{approved_codes_str}</b></font>",
                        body_style,
                    )
                ],
                [
                    Paragraph(
                        f"<b>Reviewer Verification Notes:</b><br/>{reviewer_notes}", body_style
                    )
                ],
            ]
            t_clinical = Table(clinical_grid, colWidths=[540])
            t_clinical.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                        ("PADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            story.append(t_clinical)
            story.append(Spacer(1, 20))

            # Footer Signoff
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=1,
                    color=colors.HexColor("#cbd5e1"),
                    spaceAfter=10,
                )
            )
            story.append(
                Paragraph(
                    "<i>Generated automatically by Claimora-AI Medical Coding System. Compliant with IRDAI Standard Form Requirements.</i>",
                    subtitle_style,
                )
            )

            doc.build(story)
            logger.info("Generated claim PDF at %s", output_path)
            return str(output_path)

        except Exception as exc:
            logger.error("PDF generation failed: %s", exc)
            raise ExtractionError("Failed to generate claim PDF") from exc