import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def encode(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/embed",
            json={"model": settings.ollama_embed_model, "input": text},
        )
        resp.raise_for_status()
        return resp.json()["embeddings"][0]


def is_loaded() -> bool:
    return True  # Ollama 기반이므로 lazy load 없음
