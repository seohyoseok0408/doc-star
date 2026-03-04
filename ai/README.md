# Doc-Star AI Service

FastAPI 기반 AI 서비스. Ollama(로컬 LLM) + Qdrant(벡터 DB)로 문서 임베딩/검색을 처리합니다.

---

## 아키텍처

```
[FastAPI AI Service :8000]
        │
        ├── Ollama :11434   ← 로컬 LLM (qwen2.5:1.5b) + 임베딩
        └── Qdrant :6333    ← 벡터 DB (Docker)
```

---

## 사전 설치

### 1. Docker Desktop

Qdrant 컨테이너 실행에 필요합니다.

1. https://www.docker.com/products/docker-desktop/ 에서 Windows용 인스톨러 다운로드
2. 설치 후 **Docker Desktop 실행** (시스템 트레이 고래 아이콘이 초록색이어야 합니다)

### 2. Ollama

로컬 LLM 실행 엔진입니다.

1. https://ollama.com/download 에서 Windows용 인스톨러 다운로드 후 설치
2. 설치 완료 후 **터미널(PowerShell/CMD)을 새로 열어야** PATH가 반영됩니다
3. 아래 명령으로 정상 설치 확인:

```powershell
ollama --version
```

> 설치 직후 기존 터미널에서 `ollama: 인식되지 않습니다` 오류가 뜨면 터미널을 닫고 새로 열면 해결됩니다.

4. Ollama 서버가 자동 시작되지 않았다면 수동으로 실행:

```powershell
ollama serve
```

---

## 환경 설정

### Qdrant 컨테이너 실행

프로젝트 루트(`doc-star/`)에서:

```bash
docker compose up -d qdrant
```

컨테이너 상태 확인 (`qdrant` 항목이 `running`이어야 합니다):

```bash
docker compose ps
```

### Ollama 모델 다운로드

```powershell
# 사용 모델 (약 1 GB, 한국어 지원 우수)
ollama pull qwen2.5:1.5b
```

다운로드 완료 후 목록 확인:

```powershell
ollama list
```

### 동작 확인 (선택)

대화형으로 모델이 정상 작동하는지 확인:

```powershell
ollama run qwen2.5:1.5b
```

`>>>` 프롬프트가 뜨면 성공입니다. 종료는 `/bye`.

---

## Python 환경 설정

`ai/` 디렉토리에서:

```powershell
python -m venv .venv

# 가상환경 활성화 (Windows)
.venv\Scripts\activate

pip install -r requirements.txt
```

---

## 연결 테스트

Docker(Qdrant)와 Ollama가 모두 실행 중인 상태에서:

```powershell
python check_connection.py
```

**테스트 항목:**

| 번호 | 항목 | 내용 |
|------|------|------|
| 1 | Qdrant 연결 | 컨테이너 헬스체크 |
| 2 | Ollama 연결 + 모델 | 서버 응답 + 모델 존재 여부 |
| 3 | LLM 텍스트 생성 | `/api/generate` 호출 |
| 4 | Embed → Qdrant 저장/검색 | 임베딩 생성 후 벡터 DB 저장 및 유사도 검색 |

모든 항목이 `[OK]`이면 AI 서비스 실행 준비 완료입니다.

**실패 시 체크리스트:**

| 실패 항목 | 원인 | 조치 |
|-----------|------|------|
| Qdrant 연결 | 컨테이너 미실행 | `docker compose up -d qdrant` |
| Ollama 연결 | 서버 미실행 | `ollama serve` (별도 터미널) |
| Ollama 모델 | 모델 미설치 | `ollama pull qwen2.5:1.5b` |

---

## FastAPI 서비스 실행

```powershell
cd ai/
python -m uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

헬스체크 엔드포인트:

```
GET http://localhost:8000/internal/health
```

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/internal/health` | 서비스 상태 확인 (Qdrant, Ollama, 임베딩 모델) |
| POST | `/internal/embeddings/generate` | 청크 텍스트 임베딩 생성 및 Qdrant 저장 |
| POST | `/internal/embeddings/delete` | document_id 기준 전체 청크 삭제 |
| POST | `/internal/search/semantic` | 질의 벡터 기반 유사 청크 검색 |
| POST | `/internal/search/ask` | 검색 + LLM 답변 생성 (RAG) |

---

## 환경 변수 (`.env`)

`ai/` 디렉토리에 `.env` 파일을 생성해 기본값을 재정의할 수 있습니다:

```env
# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b

# Embedding (Ollama 기반)
OLLAMA_EMBED_MODEL=qwen2.5:1.5b
EMBEDDING_DIMENSION=1536
```

---

## 디렉토리 구조

```
ai/
├── app/
│   ├── core/
│   │   ├── config.py          # 환경 변수 설정
│   │   └── dependencies.py    # DI (QdrantClient)
│   ├── routers/
│   │   ├── health.py          # GET /internal/health
│   │   ├── embeddings.py      # POST /internal/embeddings/generate|delete
│   │   ├── search.py          # POST /internal/search/semantic|ask
│   │   └── graph.py           # 그래프 관련
│   ├── services/
│   │   ├── ollama_service.py  # Ollama 헬스체크 + 텍스트 생성
│   │   ├── qdrant_service.py  # Qdrant CRUD + 벡터 검색
│   │   └── embedding_service.py # Ollama /api/embed (async)
│   └── main.py
├── check_connection.py        # 연결 테스트 스크립트
├── requirements.txt
└── README.md
```
