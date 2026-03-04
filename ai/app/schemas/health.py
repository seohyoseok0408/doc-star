from pydantic import BaseModel


class ServiceStatus(BaseModel):
    status: str  # "ok" | "unavailable"
    detail: str | None = None


class HealthResponse(BaseModel):
    qdrant: ServiceStatus
    ollama: ServiceStatus
    embedding_model: ServiceStatus
