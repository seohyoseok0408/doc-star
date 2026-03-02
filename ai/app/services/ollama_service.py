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
            if settings.ollama_model not in available:
                logger.warning(
                    "Model '%s' not found. Available: %s",
                    settings.ollama_model,
                    available,
                )
                return False
            return True
    except Exception:
        logger.warning("Ollama health check failed", exc_info=True)
        return False
