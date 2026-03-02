import logging

from fastapi import APIRouter, Depends, HTTPException
from qdrant_client import QdrantClient

from app.core.dependencies import get_qdrant_client
from app.schemas.search import (
    AskRequest,
    AskResponse,
    SearchResult,
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from app.services import embedding_service, ollama_service, qdrant_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/search", tags=["search"])


@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    body: SemanticSearchRequest,
    client: QdrantClient = Depends(get_qdrant_client),
) -> SemanticSearchResponse:
    try:
        query_vector = await embedding_service.encode(body.query)
        hits = qdrant_service.search_embeddings(client, query_vector, top_k=body.top_k)
        results = [
            SearchResult(
                document_id=hit.payload.get("document_id", 0),
                score=hit.score,
                text=hit.payload.get("text"),
            )
            for hit in hits
        ]
        return SemanticSearchResponse(results=results)
    except Exception as e:
        logger.error("Semantic search failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AskResponse)
async def ask(
    body: AskRequest,
    client: QdrantClient = Depends(get_qdrant_client),
) -> AskResponse:
    try:
        query_vector = await embedding_service.encode(body.question)
        hits = qdrant_service.search_embeddings(client, query_vector, top_k=body.top_k)

        sources = [
            SearchResult(
                document_id=hit.payload.get("document_id", 0),
                score=hit.score,
                text=hit.payload.get("text"),
            )
            for hit in hits
        ]

        context_parts = []
        for i, source in enumerate(sources, start=1):
            text = source.text or ""
            context_parts.append(f"[문서 {source.document_id}]\n{text}")
        context = "\n\n".join(context_parts)

        prompt = (
            "다음은 관련 문서 내용입니다:\n\n"
            f"{context}\n\n"
            "위 내용을 바탕으로 다음 질문에 답하세요. 문서에 없는 내용은 추측하지 마세요.\n"
            f"질문: {body.question}\n"
            "답변:"
        )

        answer = await ollama_service.generate(prompt)
        return AskResponse(answer=answer, sources=sources)
    except Exception as e:
        logger.error("Ask failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
