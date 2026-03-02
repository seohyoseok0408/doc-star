from fastapi import APIRouter

from app.schemas.search import SemanticSearchRequest, SemanticSearchResponse

router = APIRouter(prefix="/internal/search", tags=["search"])


@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(body: SemanticSearchRequest) -> SemanticSearchResponse:
    # stub: 빈 결과 반환
    return SemanticSearchResponse(results=[])
