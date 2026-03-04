import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def check_health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            if resp.status_code != 200:
                return False
            models = resp.json().get("models", [])
            available = [m["name"] for m in models]
            required = {settings.ollama_model, settings.ollama_embed_model}
            missing = required - set(available)
            if missing:
                logger.warning(
                    "Required models not found: %s. Available: %s",
                    missing,
                    available,
                )
                return False
            return True
    except Exception:
        logger.warning("Ollama health check failed", exc_info=True)
        return False


async def generate(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        return resp.json()["response"]
