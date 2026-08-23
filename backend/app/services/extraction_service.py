from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.extraction import ExtractedClaimData
from app.services.exceptions import ExtractionError

logger = get_logger(__name__)

EXTRACTION_PROMPT = """You are a clinical data extraction assistant.
Extract ONLY the patient, hospital, and clinical information present in the text below.
Do not infer or fabricate values that are not stated. Leave fields empty if not present.

CLINICAL TEXT:
{raw_text}
"""


class ExtractionService:
    def __init__(self) -> None:
        settings = get_settings()
        self._llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model_name,
            google_api_key=settings.gemini_api_key,
            temperature=0,
        ).with_structured_output(ExtractedClaimData)

    async def extract(self, raw_text: str) -> ExtractedClaimData:
        prompt = EXTRACTION_PROMPT.format(raw_text=raw_text)
        try:
            result = await self._llm.ainvoke(prompt)
        except Exception as exc:  # network errors, API errors, etc.
            logger.error("Gemini call failed: %s", exc)
            raise ExtractionError("LLM call failed") from exc

        if isinstance(result, ExtractedClaimData):
            return result

        # Fallback: some LangChain versions return a dict even with structured output
        try:
            return ExtractedClaimData.model_validate(result)
        except ValidationError as exc:
            logger.error("Gemini output failed schema validation: %s", exc)
            raise ExtractionError("LLM output did not match expected schema") from exc