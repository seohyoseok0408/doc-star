from fastapi import APIRouter

from app.schemas.graph import GraphResponse

router = APIRouter(prefix="/internal/graph", tags=["graph"])


@router.get("/data", response_model=GraphResponse)
async def get_graph_data() -> GraphResponse:
    # stub: 빈 결과 반환
    return GraphResponse(nodes=[], edges=[])
