from pydantic import BaseModel


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    document_id: int
    score: float
    text: str | None = None


class SemanticSearchResponse(BaseModel):
    results: list[SearchResult]
