import logging
import re

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# 불렛 포인트 파싱에 쓰는 접두사 패턴 (•, -, *, 1. 등)
_BULLET_PATTERN = re.compile(r"^[\s]*[•\-\*\d\.]+[\s]+", re.MULTILINE)

_SUMMARY_PROMPT_TEMPLATE = """\
[지시]
아래 [문서] 내용을 읽고 핵심 내용을 5~8개의 한국어 불렛 포인트로 요약하세요.

규칙:
- 각 줄은 반드시 "•" 기호로 시작합니다
- 불렛 한 개는 한 문장 이내로 간결하게 작성합니다
- 불렛 포인트 외에 제목, 번호, 설명 등 다른 텍스트는 출력하지 않습니다
- 반드시 5개 이상 8개 이하로 작성합니다
- 반드시 한국어로 작성합니다

[문서]
{text}

[요약]
"""


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


async def summarize(text: str) -> list[str]:
    """
    로컬 LLM을 이용해 문서를 5~8개 한국어 불렛 포인트로 요약합니다.

    Returns:
        "•" 로 시작하는 불렛 포인트 문자열 리스트
    """
    prompt = _SUMMARY_PROMPT_TEMPLATE.format(text=text.strip())
    raw = await generate(prompt)

    bullets = _parse_bullets(raw)

    # 파싱 결과가 너무 적으면 줄 단위 fallback
    if len(bullets) < 2:
        logger.warning("Bullet 파싱 결과 부족(%d개), fallback 적용", len(bullets))
        bullets = _fallback_parse(raw)

    return bullets


def _parse_bullets(raw: str) -> list[str]:
    """• 로 시작하는 줄만 추출하고, 다른 접두사(-, *, 숫자.)는 • 로 정규화."""
    lines = raw.strip().splitlines()
    result: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 이미 •로 시작
        if line.startswith("•"):
            result.append(line)
        # -, *, 숫자. 로 시작 → • 로 교체
        elif _BULLET_PATTERN.match(line):
            cleaned = _BULLET_PATTERN.sub("", line).strip()
            if cleaned:
                result.append(f"• {cleaned}")
    return result


def _fallback_parse(raw: str) -> list[str]:
    """불렛 파싱 실패 시 비어있지 않은 줄을 • 로 감싸서 반환."""
    lines = [f"• {l.strip()}" for l in raw.strip().splitlines() if l.strip()]
    return lines[:8]
