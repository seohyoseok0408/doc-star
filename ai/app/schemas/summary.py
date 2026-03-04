from pydantic import BaseModel


class SummaryRequest(BaseModel):
    document_id: int
    text: str


class SummaryResponse(BaseModel):
    document_id: int
    bullets: list[str]
    latency_ms: float
