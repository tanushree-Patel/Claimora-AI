from typing import TypedDict


class ClaimGraphState(TypedDict, total=False):
    session_id: str
    raw_text: str
    extracted_data: dict | None
    validation_errors: list[str]
    candidates: list[dict]
    review_decision: dict | None
    status: str