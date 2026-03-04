import logging
import time

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


def _hit_to_result(hit) -> SearchResult:
    payload = hit.payload or {}
    return SearchResult(
        document_id=payload.get("document_id", 0),
        chunk_id=payload.get("chunk_id"),
        chunk_index=payload.get("chunk_index"),
        score=hit.score,
        text=payload.get("text"),
    )


@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    body: SemanticSearchRequest,
    client: QdrantClient = Depends(get_qdrant_client),
) -> SemanticSearchResponse:
    try:
        t0 = time.perf_counter()
        query_vector = await embedding_service.encode(body.query)
        hits = qdrant_service.search_embeddings(client, query_vector, top_k=body.top_k)
        latency_ms = (time.perf_counter() - t0) * 1000

        results = [_hit_to_result(hit) for hit in hits]
        logger.info("Semantic search 완료: %d건, %.1f ms", len(results), latency_ms)
        return SemanticSearchResponse(results=results, latency_ms=round(latency_ms, 1))
    except Exception as e:
        logger.error("Semantic search failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AskResponse)
async def ask(
    body: AskRequest,
    client: QdrantClient = Depends(get_qdrant_client),
) -> AskResponse:
    """
    질문 → 벡터 DB 검색 → 로컬 LLM 답변 생성 (RAG 파이프라인)

    흐름:
      1. 질문 임베딩
      2. Qdrant 유사도 검색 (top_k 청크)
      3. 컨텍스트 조합 + 프롬프트 구성
      4. Ollama 로컬 LLM 답변 생성
    """
    try:
        t0 = time.perf_counter()

        # 1. 질문 임베딩
        query_vector = await embedding_service.encode(body.question)

        # 2. 유사 청크 검색
        hits = qdrant_service.search_embeddings(client, query_vector, top_k=body.top_k)
        sources = [_hit_to_result(hit) for hit in hits]

        # 3. 컨텍스트 조합
        context_parts = []
        for i, source in enumerate(sources, start=1):
            text = source.text or ""
            context_parts.append(f"[문서 {source.document_id} / 청크 {source.chunk_index}]\n{text}")
        context = "\n\n".join(context_parts)

        prompt = (
            "다음은 관련 문서 내용입니다:\n\n"
            f"{context}\n\n"
            "위 내용을 바탕으로 다음 질문에 한국어로 답하세요. "
            "문서에 없는 내용은 추측하지 마세요.\n"
            f"질문: {body.question}\n"
            "답변:"
        )

        # 4. LLM 답변 생성
        answer = await ollama_service.generate(prompt)
        latency_ms = (time.perf_counter() - t0) * 1000

        logger.info("Ask 완료: %.1f ms (검색 %d건)", latency_ms, len(sources))
        return AskResponse(answer=answer, sources=sources, latency_ms=round(latency_ms, 1))
    except Exception as e:
        logger.error("Ask failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
