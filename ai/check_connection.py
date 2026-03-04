"""
Qdrant + Ollama 연결 테스트 스크립트
실행: python check_connection.py
"""

import sys
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

# ── 설정 ────────────────────────────────────────────────
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION  = "test_collection"

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL    = "qwen2.5:1.5b"   # pull 후 사용할 모델명


# ── 헬퍼 ────────────────────────────────────────────────
def ok(msg: str) -> None:
    print(f"  [OK]  {msg}")

def fail(msg: str) -> None:
    print(f"  [FAIL] {msg}")


# ── 1. Qdrant 연결 체크 ──────────────────────────────────
def check_qdrant() -> QdrantClient | None:
    print("\n[1] Qdrant 연결 확인")
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=5)
        info = client.get_collections()
        ok(f"Qdrant 연결 성공 — 컬렉션 수: {len(info.collections)}")
        return client
    except Exception as e:
        fail(f"Qdrant 연결 실패: {e}")
        print("    → Docker가 실행 중인지, Qdrant 컨테이너가 Up 상태인지 확인하세요.")
        print("      docker compose up -d qdrant")
        return None


# ── 2. Ollama 연결 체크 ──────────────────────────────────
def check_ollama() -> bool:
    print("\n[2] Ollama 연결 확인")
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.get(f"{OLLAMA_BASE_URL}/api/tags")
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            ok(f"Ollama 연결 성공 — 설치된 모델: {models or '(없음)'}")

            if OLLAMA_MODEL not in models:
                print(f"  [WARN] '{OLLAMA_MODEL}' 모델 없음 → 먼저 pull 필요:")
                print(f"         ollama pull {OLLAMA_MODEL}")
                return False
            ok(f"'{OLLAMA_MODEL}' 모델 확인 완료")
            return True
    except httpx.ConnectError:
        fail("Ollama 서버에 연결할 수 없습니다.")
        print("    → Ollama가 설치 및 실행 중인지 확인하세요.")
        print("      ollama serve  (별도 터미널)")
        return False
    except Exception as e:
        fail(f"Ollama 오류: {e}")
        return False


# ── 3. Ollama Generate 테스트 ────────────────────────────
def check_ollama_generate() -> bool:
    print("\n[3] Ollama 텍스트 생성 테스트")
    try:
        with httpx.Client(timeout=60) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": "Hello! Reply in one sentence.",
                "stream": False,
            }
            resp = client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            resp.raise_for_status()
            text = resp.json().get("response", "").strip()
            ok(f"응답: {text[:120]}")
            return True
    except Exception as e:
        fail(f"Generate 실패: {e}")
        return False


# ── 4. Ollama Embed → Qdrant 저장/검색 ──────────────────
def check_embed_and_search(qdrant: QdrantClient) -> bool:
    print("\n[4] Ollama Embed → Qdrant 저장/검색 테스트")

    # 4-1. 임베딩 생성
    texts = [
        "FastAPI는 파이썬 기반의 빠른 웹 프레임워크입니다.",
        "Qdrant는 벡터 검색에 특화된 오픈소스 DB입니다.",
        "Ollama를 사용하면 로컬에서 LLM을 실행할 수 있습니다.",
    ]
    query = "로컬 LLM 실행 방법"

    try:
        with httpx.Client(timeout=120) as http:
            vectors: list[list[float]] = []
            for text in texts:
                r = http.post(
                    f"{OLLAMA_BASE_URL}/api/embed",
                    json={"model": OLLAMA_MODEL, "input": text},
                )
                r.raise_for_status()
                emb = r.json()["embeddings"][0]
                vectors.append(emb)
            dim = len(vectors[0])
            ok(f"임베딩 생성 완료 — 차원: {dim}")
    except Exception as e:
        fail(f"임베딩 생성 실패: {e}")
        return False

    # 4-2. 컬렉션 준비
    try:
        try:
            qdrant.delete_collection(COLLECTION)
        except Exception:
            pass
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        ok(f"컬렉션 '{COLLECTION}' 생성")
    except Exception as e:
        fail(f"컬렉션 생성 실패: {e}")
        return False

    # 4-3. 벡터 저장
    try:
        points = [
            PointStruct(id=i, vector=vec, payload={"text": text})
            for i, (vec, text) in enumerate(zip(vectors, texts))
        ]
        qdrant.upsert(collection_name=COLLECTION, points=points)
        ok(f"{len(points)}개 포인트 저장 완료")
    except Exception as e:
        fail(f"Upsert 실패: {e}")
        return False

    # 4-4. 유사 검색
    try:
        with httpx.Client(timeout=60) as http:
            r = http.post(
                f"{OLLAMA_BASE_URL}/api/embed",
                json={"model": OLLAMA_MODEL, "input": query},
            )
            r.raise_for_status()
            q_vec = r.json()["embeddings"][0]

        results = qdrant.search(
            collection_name=COLLECTION,
            query_vector=q_vec,
            limit=2,
        )
        ok(f"검색 완료 — 쿼리: '{query}'")
        for hit in results:
            print(f"      score={hit.score:.4f}  text={hit.payload['text'][:60]}")
        return True
    except Exception as e:
        fail(f"검색 실패: {e}")
        return False


# ── 메인 ────────────────────────────────────────────────
def main() -> None:
    print("=" * 55)
    print("  Doc-Star AI — Qdrant + Ollama 연결 테스트")
    print("=" * 55)

    results: dict[str, bool] = {}

    qdrant = check_qdrant()
    results["qdrant"] = qdrant is not None

    ollama_ok = check_ollama()
    results["ollama"] = ollama_ok

    if ollama_ok:
        results["generate"] = check_ollama_generate()
    else:
        results["generate"] = False
        print("\n[3] Ollama 모델 미설치 — Generate 테스트 건너뜀")

    if qdrant and ollama_ok:
        results["embed_search"] = check_embed_and_search(qdrant)
    else:
        results["embed_search"] = False
        print("\n[4] 선행 조건 미충족 — Embed/Search 테스트 건너뜀")

    # ── 결과 요약 ──
    print("\n" + "=" * 55)
    print("  결과 요약")
    print("=" * 55)
    labels = {
        "qdrant":       "Qdrant 연결",
        "ollama":       "Ollama 연결 + 모델",
        "generate":     "LLM 텍스트 생성",
        "embed_search": "Embed → Qdrant 저장/검색",
    }
    all_ok = True
    for key, label in labels.items():
        status = "OK  " if results[key] else "FAIL"
        print(f"  [{status}] {label}")
        if not results[key]:
            all_ok = False

    print("=" * 55)
    if all_ok:
        print("  모든 테스트 통과! AI 서비스 실행 준비 완료.")
    else:
        print("  일부 테스트 실패. 위 안내를 따라 조치 후 재실행하세요.")
    print()

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
