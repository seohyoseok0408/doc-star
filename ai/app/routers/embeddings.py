import logging

from fastapi import APIRouter, Depends, HTTPException
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from app.core.dependencies import get_qdrant_client
from app.schemas.embeddings import (
    BatchChunkResult,
    BatchEmbeddingRequest,
    BatchEmbeddingResponse,
    EmbeddingDeleteRequest,
    EmbeddingDeleteResponse,
    EmbeddingRequest,
    EmbeddingResponse,
)
from app.services import embedding_service, qdrant_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/embeddings", tags=["embeddings"])


@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embedding(
    body: EmbeddingRequest,
    client: QdrantClient = Depends(get_qdrant_client),
) -> EmbeddingResponse:
    try:
        qdrant_service.ensure_collection(client)
        vector = await embedding_service.encode(body.text)
        qdrant_service.upsert_embedding(
            client,
            chunk_id=body.chunk_id,
            document_id=body.document_id,
            vector=vector,
            text=body.text,
        )
        return EmbeddingResponse(
            document_id=body.document_id,
            chunk_id=body.chunk_id,
            success=True,
        )
    except Exception as e:
        logger.error("Embedding generation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchEmbeddingResponse)
async def batch_generate_embeddings(
    body: BatchEmbeddingRequest,
    client: QdrantClient = Depends(get_qdrant_client),
) -> BatchEmbeddingResponse:
    """
    백엔드(Java)에서 chunking 완료된 청크 목록을 받아
    임베딩을 생성하고 Qdrant에 일괄 적재합니다.

    - 청크별로 순차 임베딩 후 단일 batch upsert
    - 개별 청크 실패 시 해당 청크만 failed 처리 (전체 실패 방지)
    """
    qdrant_service.ensure_collection(client)

    results: list[BatchChunkResult] = []
    points: list[PointStruct] = []

    for chunk in body.chunks:
        try:
            vector = await embedding_service.encode(chunk.text)
            payload = {
                "document_id": body.document_id,
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
            }
            if chunk.start_pos is not None:
                payload["start_pos"] = chunk.start_pos
            if chunk.end_pos is not None:
                payload["end_pos"] = chunk.end_pos

            points.append(
                PointStruct(id=chunk.chunk_id, vector=vector, payload=payload)
            )
            results.append(
                BatchChunkResult(chunk_id=chunk.chunk_id, chunk_index=chunk.chunk_index, success=True)
            )
        except Exception as e:
            logger.error(
                "Chunk embedding failed [doc=%d chunk=%d]: %s",
                body.document_id,
                chunk.chunk_id,
                e,
                exc_info=True,
            )
            results.append(
                BatchChunkResult(
                    chunk_id=chunk.chunk_id,
                    chunk_index=chunk.chunk_index,
                    success=False,
                    detail=str(e),
                )
            )

    # 성공한 포인트만 일괄 적재
    if points:
        try:
            qdrant_service.batch_upsert_embeddings(client, points)
            logger.info(
                "Batch upsert 완료 [doc=%d] %d/%d 청크",
                body.document_id,
                len(points),
                len(body.chunks),
            )
        except Exception as e:
            logger.error("Qdrant batch upsert failed: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail=f"Qdrant upsert failed: {e}")

    succeeded = sum(1 for r in results if r.success)
    return BatchEmbeddingResponse(
        document_id=body.document_id,
        total=len(body.chunks),
        succeeded=succeeded,
        failed=len(body.chunks) - succeeded,
        results=results,
    )


@router.post("/delete", response_model=EmbeddingDeleteResponse)
async def delete_embedding(
    body: EmbeddingDeleteRequest,
    client: QdrantClient = Depends(get_qdrant_client),
) -> EmbeddingDeleteResponse:
    try:
        qdrant_service.delete_embedding(client, body.document_id)
        return EmbeddingDeleteResponse(document_id=body.document_id, success=True)
    except Exception as e:
        logger.error("Embedding deletion failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
