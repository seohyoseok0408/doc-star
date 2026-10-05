from pydantic import BaseModel


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    document_id: int
    chunk_id: int | None = None
    chunk_index: int | None = None
    score: float
    text: str | None = None


class SemanticSearchResponse(BaseModel):
    results: list[SearchResult]
    latency_ms: float


class AskRequest(BaseModel):
    question: str
    top_k: int = 3


class AskResponse(BaseModel):
    answer: str
    sources: list[SearchResult]
    latency_ms: float
