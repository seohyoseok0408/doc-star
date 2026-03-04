import logging

from fastapi import FastAPI

from app.core.config import settings
from app.routers import embeddings, graph, health, search

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Doc-Star AI Service",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(embeddings.router)
app.include_router(search.router)
app.include_router(graph.router)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Doc-Star AI Service starting up")
    logger.info("Qdrant: %s:%s", settings.qdrant_host, settings.qdrant_port)
    logger.info("Ollama: %s", settings.ollama_base_url)
    logger.info("Embedding model: %s", settings.embedding_model)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
