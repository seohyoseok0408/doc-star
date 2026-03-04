import logging
import time

from fastapi import APIRouter, HTTPException

from app.schemas.summary import SummaryRequest, SummaryResponse
from app.services import ollama_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/summary", tags=["summary"])


@router.post("/document", response_model=SummaryResponse)
async def summarize_document(body: SummaryRequest) -> SummaryResponse:
    """
    백엔드에서 전달한 문서 전문을 로컬 LLM으로 요약합니다.

    - 5~8개 한국어 불렛 포인트 반환
    - latency_ms: LLM 호출 포함 전체 처리 시간(ms)
    """
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="text가 비어 있습니다.")

    try:
        t0 = time.perf_counter()
        bullets = await ollama_service.summarize(body.text)
        latency_ms = (time.perf_counter() - t0) * 1000

        logger.info(
            "Summary 완료 [doc=%d] %d개 불렛, %.1f ms",
            body.document_id,
            len(bullets),
            latency_ms,
        )
        return SummaryResponse(
            document_id=body.document_id,
            bullets=bullets,
            latency_ms=round(latency_ms, 1),
        )
    except Exception as e:
        logger.error("Summary failed [doc=%d]: %s", body.document_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
