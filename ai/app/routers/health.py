from fastapi import APIRouter, Depends
from qdrant_client import QdrantClient

from app.core.config import settings
from app.core.dependencies import get_qdrant_client
from app.schemas.health import HealthResponse, ServiceStatus
from app.services import ollama_service, qdrant_service

router = APIRouter(prefix="/internal", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    client: QdrantClient = Depends(get_qdrant_client),
) -> HealthResponse:
    qdrant_ok = qdrant_service.check_health(client)
    ollama_ok = await ollama_service.check_health()

    return HealthResponse(
        qdrant=ServiceStatus(
            status="ok" if qdrant_ok else "unavailable",
        ),
        ollama=ServiceStatus(
            status="ok" if ollama_ok else "unavailable",
        ),
        embedding_model=ServiceStatus(
            status="ok" if ollama_ok else "unavailable",
            detail=None if ollama_ok else f"Ollama embed model '{settings.ollama_embed_model}' unavailable",
        ),
    )
