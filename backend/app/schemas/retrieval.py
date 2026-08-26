
from pydantic import BaseModel


class CodeCandidate(BaseModel):
    code_system: str
    code: str
    display_name: str
    score: float
    matched_via: list[str]  # e.g. ["vector"], ["trigram"], or ["vector", "trigram"]


class RetrievalResult(BaseModel):
    query: str
    candidates: list[CodeCandidate]