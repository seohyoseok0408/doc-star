import logging

from fastapi import APIRouter, Depends, HTTPException
from qdrant_client import QdrantClient

from app.core.dependencies import get_qdrant_client
from app.schemas.embeddings import (
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
