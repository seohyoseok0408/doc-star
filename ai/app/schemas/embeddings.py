from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    document_id: int
    chunk_id: int
    text: str


class EmbeddingResponse(BaseModel):
    document_id: int
    chunk_id: int
    success: bool
    detail: str | None = None


class EmbeddingDeleteRequest(BaseModel):
    document_id: int


class EmbeddingDeleteResponse(BaseModel):
    document_id: int
    success: bool
    detail: str | None = None
