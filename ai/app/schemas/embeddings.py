from pydantic import BaseModel


# ── 단건 ────────────────────────────────────────────────────────
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


# ── 배치 ─────────────────────────────────────────────────────────
class ChunkItem(BaseModel):
    """백엔드(Java)에서 전달되는 청크 단위. chunking은 백엔드 담당."""
    chunk_id: int
    chunk_index: int
    text: str
    start_pos: int | None = None
    end_pos: int | None = None


class BatchEmbeddingRequest(BaseModel):
    document_id: int
    chunks: list[ChunkItem]


class BatchChunkResult(BaseModel):
    chunk_id: int
    chunk_index: int
    success: bool
    detail: str | None = None


class BatchEmbeddingResponse(BaseModel):
    document_id: int
    total: int
    succeeded: int
    failed: int
    results: list[BatchChunkResult]
