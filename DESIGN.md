# Doc-Star — 프로젝트 기획 · 설계 · 개발 로드맵

> **최종 업데이트**: 2026-02-11
> **프로젝트 타입**: 2인 포트폴리오 프로젝트
> **한 줄 요약**: PDF 문서 업로드 → AI 임베딩 분석 → 문서 연관관계 인터랙티브 그래프 시각화

---

## 1. 프로젝트 개요

### 1.1 Doc-Star란?

PDF 문서를 업로드하면 AI가 임베딩 분석으로 문서 간 연관관계를 자동으로 파악하고,
이를 **D3.js 인터랙티브 그래프**로 시각화하는 웹 애플리케이션.

### 1.2 핵심 사용자 시나리오

1. 사용자가 PDF 문서를 업로드한다
2. AI가 문서 내용을 분석해 임베딩 벡터를 생성한다
3. 문서 간 유사도를 계산해 연관관계를 만든다
4. 연관관계를 인터랙티브 그래프로 시각화한다 (줌, 드래그, 클러스터링)
5. 키워드 검색과 AI 시맨틱 검색으로 문서를 찾을 수 있다

### 1.3 현재 상태 (2026-02-11)

- 프론트엔드: JWT 인증(로그인, 회원가입, 토큰 갱신)만 구현됨
- 백엔드: 미개발
- 나머지 기능(문서 관리, 그래프, 검색, 관리자)은 빈 상태

---

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
[React SPA] ──→ [Spring Boot API 서버] ──→ [PostgreSQL]
  프론트엔드           ↕ (내부 통신)
                [Python AI 서비스 (FastAPI)]
                       ↕
                [Qdrant 벡터DB] + [Ollama LLM 서버]
```

### 2.2 서버 역할 분담

| 서버 | 기술 스택 | 담당 영역 | 개발 포트 |
|------|-----------|-----------|-----------|
| **프론트엔드** | React + TypeScript + Vite | UI, 사용자 인터랙션 | 5173 |
| **메인 API** | Java Spring Boot | 인증, 문서 CRUD, 관리자, API 게이트웨이 | 8080 |
| **AI 서비스** | Python FastAPI | 임베딩, LLM 추론, 벡터 검색 | 8000 |
| **벡터 DB** | Qdrant | 임베딩 벡터 저장/검색 | 6333 |
| **LLM 서버** | Ollama | 모델 서빙 (Qwen2.5 3B) | 11434 |
| **RDB** | PostgreSQL | 사용자, 문서 메타데이터, 로그 | 5432 |

### 2.3 핵심 설계 원칙

- **프론트엔드는 Spring Boot만 바라본다** — Python AI 서비스의 존재를 몰라도 됨
- **Spring Boot가 API 게이트웨이** — AI 관련 요청은 Spring Boot가 Python에 내부 위임
- **Python AI 서비스는 외부에 노출하지 않는다** — 오직 Spring Boot에서만 접근

---

## 3. AI 파이프라인 설계

### 3.1 AI 기술 스택

| 구분 | 선택 | 용도 |
|------|------|------|
| **임베딩 모델** | BGE-M3 | 문서 텍스트 → 벡터 변환 (다국어 지원) |
| **LLM** | Qwen2.5 3B | 문서 요약, 토픽 분류 등 (향후 확장) |
| **파인튜닝** | QLoRA | 경량 파인튜닝으로 도메인 특화 |
| **모델 서빙** | Ollama | 로컬 LLM 서빙 환경 |
| **벡터 DB** | Qdrant | 임베딩 저장, 유사도 검색 |
| **컨테이너** | Docker | LLM + Qdrant + Ollama 통합 관리 |

### 3.2 주요 데이터 흐름

**문서 업로드**:
프론트 → Spring Boot(파일 저장 + DB 저장) → Python(PDF 텍스트 추출 → BGE-M3 임베딩 → Qdrant 저장) → 상태 업데이트(completed)

**시맨틱 검색**:
프론트 → Spring Boot → Python(쿼리 임베딩 → Qdrant 유사도 검색) → Spring Boot(문서 메타데이터 조합) → 프론트

**그래프 데이터**:
프론트 → Spring Boot → Python(벡터 유사도 계산 → 노드/엣지/토픽 생성) → 프론트

---

## 4. 기능 요구사항

### 4.1 인증 (Auth)

| 기능 | 설명 | 담당 |
|------|------|------|
| 회원가입 | username, password, nickname, email 입력 | Spring Boot |
| 로그인 | JWT access token 발급 + refresh token 쿠키 | Spring Boot |
| 토큰 갱신 | refresh token으로 access token 재발급 | Spring Boot |
| 로그아웃 | refresh token 쿠키 삭제 | Spring Boot |
| 내 정보 조회 | 현재 로그인한 사용자 정보 반환 | Spring Boot |

### 4.2 문서 관리 (Documents)

| 기능 | 설명 | 담당 |
|------|------|------|
| 문서 업로드 | PDF 파일 + 메타데이터(제목, 설명, 태그) | Spring Boot → Python |
| 문서 목록 조회 | 페이지네이션, 정렬 지원 | Spring Boot |
| 문서 상세 조회 | 메타데이터 + 임베딩 상태 | Spring Boot |
| 문서 수정 | 제목, 설명, 태그 수정 | Spring Boot |
| 문서 삭제 | DB 삭제 + Qdrant 벡터 삭제 | Spring Boot → Python |
| 임베딩 상태 표시 | pending → processing → completed / failed | Spring Boot |

### 4.3 그래프 시각화 (Graph) ★ 핵심 포트폴리오 기능

| 기능 | 설명 | 담당 |
|------|------|------|
| 그래프 데이터 로드 | 노드(문서) + 엣지(유사도) + 토픽(클러스터) | Python → Spring Boot |
| Force 시뮬레이션 | D3 force layout으로 자동 배치 | 프론트 (D3.js) |
| 줌/패닝 | 마우스 휠 줌, 드래그 패닝 | 프론트 (D3.js) |
| 노드 드래그 | 개별 노드 위치 이동 | 프론트 (D3.js) |
| 토픽 클러스터링 | 같은 토픽 문서끼리 색상 구분 + 모여서 배치 | 프론트 (커스텀 포스) |
| 노드 클릭 | 사이드바에 문서 상세 정보 표시 | 프론트 |
| 토픽 필터 | 특정 토픽만 하이라이트 | 프론트 |
| 엣지 두께 | 유사도 weight에 비례 | 프론트 |

### 4.4 검색 (Search)

| 기능 | 설명 | 담당 |
|------|------|------|
| 키워드 검색 | DB 전문검색 (PostgreSQL Full-Text Search) | Spring Boot |
| 시맨틱 검색 | 쿼리 임베딩 → Qdrant 유사도 검색 | Python → Spring Boot |
| 검색 모드 전환 | 키워드 ↔ 시맨틱 토글 | 프론트 |
| 검색 필터 | 태그, 날짜 범위 | 프론트 + Spring Boot |
| 결과 하이라이트 | 검색어 매칭 부분 강조 | 프론트 |
| URL 파라미터 동기화 | 뒤로가기 시 검색 상태 유지 | 프론트 |

### 4.5 관리자 대시보드 (Admin)

| 기능 | 설명 | 담당 |
|------|------|------|
| ADMIN 권한 체크 | 관리자만 접근 가능 | Spring Boot |
| 시스템 상태 | DB, AI 서비스, Qdrant, Ollama 연결 상태 | Spring Boot → Python |
| 통계 카드 | 총 문서 수, 유저 수, 임베딩 현황 | Spring Boot |
| 배치 로그 | 임베딩 처리 이력 (5초 자동 갱신) | Spring Boot |
| 임베딩 재생성 | 전체 문서 임베딩 일괄 재생성 트리거 | Spring Boot → Python |

---

## 5. API 설계 (프론트엔드 기준)

> 프론트엔드는 모든 요청을 `/api/*`로 보냄 → Spring Boot가 단일 진입점
> 공통 응답 형식: `{ "message": "...", "data": T }`
> 인증: `Authorization: Bearer <token>` 헤더 / Refresh Token: HTTP-only 쿠키

### 5.1 인증 API

| 메서드 | 경로 | 설명 | 비고 |
|--------|------|------|------|
| POST | `/api/auth/login` | 로그인 | 응답: access_token + Set-Cookie: refresh_token |
| POST | `/api/auth/register` | 회원가입 | |
| POST | `/api/auth/refresh` | 토큰 갱신 | Cookie에서 refresh_token 사용 |
| POST | `/api/auth/logout` | 로그아웃 | refresh_token 쿠키 삭제 |
| GET | `/api/auth/me` | 내 정보 | |

### 5.2 문서 API

| 메서드 | 경로 | 설명 | 비고 |
|--------|------|------|------|
| GET | `/api/documents` | 문서 목록 | ?page, size, sort |
| GET | `/api/documents/:id` | 문서 상세 | |
| POST | `/api/documents` | 문서 업로드 | multipart/form-data → 비동기 임베딩 |
| PATCH | `/api/documents/:id` | 문서 수정 | title, description, tags |
| DELETE | `/api/documents/:id` | 문서 삭제 | DB + 벡터 동시 삭제 |

### 5.3 그래프 API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/graph` | 그래프 데이터 (nodes, edges, topics) |
| GET | `/api/graph/topics` | 토픽 목록 |

### 5.4 검색 API

| 메서드 | 경로 | 설명 | 비고 |
|--------|------|------|------|
| GET | `/api/search` | 검색 | ?q, mode(keyword/semantic), page, size |

### 5.5 관리자 API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/admin/health` | 시스템 건강 상태 (DB, AI, Qdrant, Ollama) |
| GET | `/api/admin/stats` | 통계 (문서 수, 유저 수, 임베딩 현황) |
| GET | `/api/admin/logs` | 배치 로그 (?page, size) |
| POST | `/api/admin/embeddings/regenerate` | 임베딩 재생성 |

### 5.6 Java ↔ Python 내부 통신 (프론트에서 호출하지 않음)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/internal/embeddings/generate` | 문서 임베딩 생성 요청 |
| POST | `/internal/embeddings/delete` | 벡터 삭제 |
| POST | `/internal/search/semantic` | 시맨틱 검색 |
| GET | `/internal/graph/data` | 그래프 데이터 조회 |
| POST | `/internal/embeddings/regenerate` | 전체 재생성 |
| GET | `/internal/health` | AI 서비스 헬스체크 |

---

## 6. 프론트엔드 설계

### 6.1 기술 스택

| 영역 | 선택 | 이유 |
|------|------|------|
| 프레임워크 | React + TypeScript + Vite | 기존 구성 유지 |
| 서버 상태 | TanStack Query v5 | 캐싱, 자동 리페칭, 로딩/에러 관리 |
| 클라이언트 상태 | Zustand v5 | 경량, 그래프 UI 상태에 적합 |
| 그래프 시각화 | D3.js (force + zoom) | 포트폴리오 임팩트, 세밀한 제어 |
| 폼 관리 | react-hook-form + zod | 유효성 검사 통합 |
| 파일 업로드 | react-dropzone | headless, 커스텀 UI |
| 데이터 테이블 | TanStack Table v8 | headless, shadcn/ui 조합 |
| UI 컴포넌트 | shadcn/ui | 기존 구성 유지 |
| 토스트 | sonner | shadcn/ui 공식 추천 |

### 6.2 라우트 맵

| 경로 | 페이지 | 인증 | 설명 |
|------|--------|------|------|
| `/login` | LoginPage | X | 로그인 |
| `/register` | RegisterPage | X | 회원가입 |
| `/` | → `/documents` 리다이렉트 | O | 홈 |
| `/documents` | DocumentsPage | O | 문서 목록 (테이블/그리드) |
| `/documents/:id` | DocumentDetailPage | O | 문서 상세 |
| `/graph` | GraphPage | O | 문서 그래프 탐색 ★ |
| `/search` | SearchPage | O | 검색 |
| `/admin` | AdminDashboardPage | O (ADMIN) | 관리자 대시보드 |
| `*` | NotFound | - | 404 |

### 6.3 폴더 구조 (Feature-based)

```
src/
├── main.tsx
├── app/providers.tsx                  # QueryClient + Toaster 합성
├── components/
│   ├── ui/                            # shadcn/ui 컴포넌트
│   ├── layout/                        # Layout, Sidebar, Header
│   └── common/                        # loading-spinner, empty-state, confirm-dialog
├── features/
│   ├── auth/                          # 인증 (components, pages, api, hooks, stores, types)
│   ├── documents/                     # 문서 관리
│   ├── graph/                         # 그래프 시각화 ★
│   ├── search/                        # 검색
│   └── admin/                         # 관리자
├── hooks/                             # 공유 훅 (use-mobile, use-debounce)
├── lib/                               # api-client, auth, query-client, query-keys, utils
├── types/                             # 공유 타입 (ApiResponse, PaginatedResponse)
├── routes/                            # AppRoutes, ProtectedRoute
└── styles/
```

### 6.4 현재 코드 문제점 → 해결 방향

| 문제 | 해결 |
|------|------|
| Authorization 헤더에서 토큰 추출 | → JSON body에서 access_token 파싱 |
| LoginPage, RegisterPage가 raw axios 사용 | → 공통 apiClient 통일 |
| 에러/성공 알림이 `alert()` | → sonner toast 전환 |
| 인증 상태가 localStorage 직접 조회 | → Zustand auth store 도입 |
| API 호출 결과 캐싱 없음 | → TanStack Query 도입 |
| 토큰 갱신 URL `/jwt/refresh` | → `/api/auth/refresh` 변경 |
| 개발환경 CORS 대응 없음 | → Vite proxy → `localhost:8080` |

---

## 7. 백엔드 설계

### 7.1 Java Spring Boot (메인 API 서버)

| 모듈 | 설명 |
|------|------|
| Auth | JWT 발급/검증, 회원 관리, Spring Security |
| Document | 문서 CRUD, 파일 저장(로컬/S3), 메타데이터 관리 |
| Search (keyword) | PostgreSQL Full-Text Search |
| Admin | 시스템 상태, 배치 로그, 사용자 관리 |
| AI Gateway | Python AI 서비스 호출용 내부 HTTP 클라이언트 (WebClient) |

주요 의존성: Spring Boot 3.x, Spring Security + JWT, Spring Data JPA + PostgreSQL, Spring WebFlux WebClient

### 7.2 Python FastAPI (AI 서비스)

| 모듈 | 설명 |
|------|------|
| 임베딩 생성 | BGE-M3로 문서 텍스트 → 벡터 변환 |
| LLM 추론 | Qwen2.5 3B (Ollama 서빙), QLoRA 파인튜닝 |
| 벡터DB 관리 | Qdrant에 임베딩 CRUD |
| 시맨틱 검색 | 쿼리 임베딩 → Qdrant 유사도 검색 |
| 그래프 데이터 | 벡터 유사도 기반 노드/엣지/토픽 생성 |

주요 의존성: FastAPI + Uvicorn, sentence-transformers (BGE-M3), ollama client, qdrant-client, PyPDF2 / pdfplumber

### 7.3 Docker 구성

| 컨테이너 | 이미지 | 설명 |
|-----------|--------|------|
| api | 커스텀 빌드 | Spring Boot (8080) |
| ai-service | 커스텀 빌드 | Python FastAPI (8000), GPU 사용 시 device 설정 |
| qdrant | qdrant/qdrant | 벡터DB (6333) |
| ollama | ollama/ollama | LLM 서버 (11434) |
| postgres | postgres:16 | RDB (5432) |

---

## 8. 개발 로드맵

> 아래 순서대로 진행. **위에 있을수록 먼저** 해야 합니다.
> 각 Phase 안에서도 Step 순서를 지켜주세요.

---

### 🔴 Phase 0: 프론트엔드 기반 세팅 + 기존 코드 마이그레이션

> **다른 건 다 미루더라도 이것부터.**
> 기존 인증 코드를 새 아키텍처에 맞게 정리하고, 앞으로 모든 기능이 올라갈 기반을 깐다.

| Step | 할 일 | 상세 |
|------|--------|------|
| 0-1 | 새 의존성 설치 | TanStack Query, Zustand, react-hook-form, zod, D3, react-dropzone, TanStack Table, sonner |
| 0-2 | 폴더 구조 재배치 | Feature-based 구조로 기존 파일 이동 (utils→lib, pages→features/*/pages) |
| 0-3 | 공유 인프라 파일 생성 | api.types.ts, query-client.ts, query-keys.ts, providers.tsx |
| 0-4 | 인증 코드 리팩토링 | extractTokenFromHeader 삭제, apiClient 통일, alert→toast, Zustand auth store |
| 0-5 | Vite 프록시 설정 | `/api` → `localhost:8080` (Spring Boot) |
| 0-6 | .env.example 작성 | VITE_BACKEND_API_BASE_URL |
| 0-7 | 라우트 업데이트 | `/` → `/documents` 리다이렉트, 새 페이지 라우트 추가 (빈 페이지라도) |
| 0-8 | 사이드바 메뉴 업데이트 | 문서, 그래프, 검색, 관리 메뉴 추가 |

✅ **완료 기준**: `npm run build` 성공, 로그인/회원가입 정상, toast 동작, 모든 라우트 접근 가능

---

### 🟠 Phase 1: 문서 관리 (CRUD)

> **문서가 있어야 그래프도 검색도 된다. 가장 기본.**

| Step | 할 일 | 상세 |
|------|--------|------|
| 1-1 | 타입 + API 함수 정의 | document.types.ts, documents.api.ts |
| 1-2 | 문서 목록 페이지 | 테이블 뷰 + 그리드 뷰 토글 |
| 1-3 | 문서 업로드 | 드래그앤드롭 + 진행률 표시 |
| 1-4 | 문서 상세 페이지 | PDF 프리뷰 + 메타데이터 편집 |
| 1-5 | 문서 삭제 | 확인 다이얼로그 → 삭제 |
| 1-6 | shadcn/ui 추가 설치 | badge, dialog, dropdown-menu, progress, select, table, tabs, toggle-group |

✅ **완료 기준**: 업로드 → 목록 → 상세 → 수정 → 삭제 풀 사이클 동작

---

### 🟡 Phase 2: 그래프 시각화 ★ (핵심 포트폴리오 기능)

> **이 프로젝트의 차별점. D3.js force simulation으로 문서 연관관계 시각화.**

| Step | 할 일 | 상세 |
|------|--------|------|
| 2-1 | 타입 + API 정의 | GraphNode, GraphEdge, Topic, graph.api.ts |
| 2-2 | Zustand 그래프 스토어 | selectedNode, activeTopic, zoom 상태 |
| 2-3 | D3 Force Simulation | forceLink, forceManyBody, forceCenter, forceCollide |
| 2-4 | 토픽 클러스터링 | 커스텀 포스 함수 (같은 토픽끼리 모임) |
| 2-5 | 캔버스 + 노드/엣지 렌더링 | React SVG + D3 하이브리드 |
| 2-6 | 인터랙션 | 줌/패닝 (d3-zoom), 노드 드래그 (d3-drag) |
| 2-7 | 노드 클릭 → 사이드바 | 선택 문서 상세 표시 |
| 2-8 | 토픽 범례 + 필터 | 색상 범례, 클릭 시 하이라이트 |

✅ **완료 기준**: 그래프 로딩 → 렌더링 → 줌/드래그 → 클러스터링 → 노드 클릭 상세

---

### 🟢 Phase 3: 검색

> **문서가 많아지면 검색이 필요하다.**

| Step | 할 일 | 상세 |
|------|--------|------|
| 3-1 | 타입 + API 정의 | search.types.ts, search.api.ts |
| 3-2 | 검색 바 + 디바운스 | 300ms 디바운스 후 API 호출 |
| 3-3 | 키워드/시맨틱 모드 전환 | 토글 UI |
| 3-4 | 검색 결과 표시 | 제목, 스니펫(하이라이트), 관련도 점수, 태그 |
| 3-5 | 검색 필터 | 태그, 날짜 범위 |
| 3-6 | URL 파라미터 동기화 | 뒤로가기 시 검색 유지 |

✅ **완료 기준**: 검색 → 결과 표시, 모드 전환, URL 동기화

---

### 🔵 Phase 4: 관리자 대시보드

> **ADMIN 전용. 시스템 모니터링.**

| Step | 할 일 | 상세 |
|------|--------|------|
| 4-1 | 타입 + API 정의 | admin.types.ts, admin.api.ts |
| 4-2 | ADMIN 권한 체크 | ProtectedRoute role 기반 접근 제어 |
| 4-3 | 통계 카드 | 총 문서, 유저, 임베딩 pending/completed |
| 4-4 | 시스템 상태 카드 | DB, AI, Qdrant, Ollama 연결 상태 |
| 4-5 | 배치 로그 테이블 | 5초 자동 갱신 |
| 4-6 | 임베딩 재생성 버튼 | 전체 재생성 트리거 |

✅ **완료 기준**: ADMIN만 접근, 상태 표시, 로그 갱신, 재생성 동작

---

### 🟣 Phase 5: UX 폴리싱

> **완성도 높이는 마무리.**

| 할 일 | 설명 |
|--------|------|
| 글로벌 검색 | Ctrl+K → 검색 다이얼로그 |
| 로딩 스켈레톤 | 각 페이지 로딩 시 스켈레톤 UI |
| 에러 바운더리 | React ErrorBoundary |
| 빈 상태 UI | 데이터 없을 때 안내 |
| 모바일 반응형 | 사이드바, 테이블, 그래프 대응 |

---

## 9. 백엔드 개발 로드맵

> 프론트엔드 Phase와 병행. 맞물리는 Phase를 확인하세요.

---

### 🔴 BE Phase 0: Spring Boot 프로젝트 세팅

| 할 일 | 상세 |
|--------|------|
| 프로젝트 초기화 | Spring Boot 3.x + Gradle/Maven |
| DB 설정 | PostgreSQL 연결, JPA 엔티티 (User, Document, BatchLog) |
| Spring Security + JWT | 인증/인가 필터, 토큰 발급/검증 |
| CORS 설정 | 프론트엔드 도메인 허용 |
| API 응답 형식 통일 | `{ message, data }` 공통 래퍼 |

**→ 프론트 Phase 0과 맞물림** (인증 연동)

---

### 🟠 BE Phase 1: 문서 CRUD + 파일 관리

| 할 일 | 상세 |
|--------|------|
| Document 엔티티 | id, title, description, fileName, fileSize, tags, topics, embeddingStatus |
| 파일 업로드/다운로드 | MultipartFile 처리, 로컬 또는 S3 |
| 문서 CRUD API | GET/POST/PATCH/DELETE |
| 페이지네이션 | Spring Data Pageable |

**→ 프론트 Phase 1과 맞물림** (문서 관리)

---

### 🟡 BE Phase 2: Python AI 서비스 구축

| 할 일 | 상세 |
|--------|------|
| FastAPI 프로젝트 세팅 | 프로젝트 초기화, Uvicorn 설정 |
| Ollama 환경 구성 | Docker로 Ollama 실행, Qwen2.5 3B 모델 pull |
| BGE-M3 임베딩 파이프라인 | sentence-transformers로 임베딩 생성 |
| Qdrant 연동 | 컬렉션 생성, 벡터 CRUD |
| 내부 API 구현 | /internal/* 엔드포인트 전체 |
| Spring Boot AI Gateway | WebClient로 Python 호출하는 클라이언트 |

**→ 프론트 Phase 2와 맞물림** (그래프 데이터)

---

### 🟢 BE Phase 3: 검색 + 그래프 데이터

| 할 일 | 상세 |
|--------|------|
| 키워드 검색 | PostgreSQL Full-Text Search |
| 시맨틱 검색 연동 | Java → Python → Qdrant 유사도 검색 |
| 그래프 데이터 API | 벡터 유사도 기반 노드/엣지/토픽 생성 |

**→ 프론트 Phase 2, 3과 맞물림**

---

### 🔵 BE Phase 4: 관리자 + 모니터링

| 할 일 | 상세 |
|--------|------|
| 시스템 헬스체크 | DB + AI + Qdrant + Ollama 상태 |
| 통계 API | 문서 수, 유저 수, 임베딩 현황 |
| 배치 로그 | 임베딩 처리 이력 저장/조회 |
| 임베딩 재생성 | 전체 재처리 트리거 |

**→ 프론트 Phase 4와 맞물림**

---

### 🟤 BE Phase 5: LLM 파인튜닝 (Qwen2.5 3B + QLoRA)

| 할 일 | 상세 |
|--------|------|
| 학습 데이터 준비 | 문서 기반 QA 쌍 또는 요약 데이터셋 |
| QLoRA 파인튜닝 | PEFT + bitsandbytes 경량 파인튜닝 |
| Ollama 커스텀 모델 등록 | 파인튜닝 결과 Ollama 배포 |
| LLM 추론 API | 문서 요약, 질의응답 (향후 확장) |

**→ 독립적으로 진행 가능**

---

## 10. 프론트 ↔ 백엔드 타임라인

```
[FE Phase 0] 기반 세팅 → [FE Phase 1] 문서 → [FE Phase 2] 그래프 ★ → [FE Phase 3] 검색 → [FE Phase 4] 관리자 → [FE Phase 5] 폴리싱
     ↕ 동시                 ↕ 맞물림           ↕ 맞물림               ↕ 맞물림           ↕ 맞물림
[BE Phase 0] Spring Boot → [BE Phase 1] 문서 → [BE Phase 2] AI 서비스 → [BE Phase 3] 검색 → [BE Phase 4] 관리자 → [BE Phase 5] LLM
```

**순서 요약**:
1. **FE Phase 0 + BE Phase 0** 동시 착수 → 인증 연결 확인
2. **FE Phase 1 + BE Phase 1** → 문서 풀 사이클
3. **BE Phase 2** (AI 서비스) 먼저 → **FE Phase 2** (그래프) 연결
4. 이후 검색 → 관리자 → 폴리싱 순서
5. **BE Phase 5** (LLM 파인튜닝)는 독립 진행 가능

---

## 11. 검증 체크리스트

### Phase 0
- [ ] `npm run build` 타입 에러 없이 성공
- [ ] 로그인 → 토큰 발급 → 인증 상태 유지
- [ ] 회원가입 → 로그인 → 페이지 접근 가능
- [ ] toast 알림 정상 (alert 없음)
- [ ] Vite 프록시 → Spring Boot 연결

### Phase 1
- [ ] 문서 업로드 → 목록 표시
- [ ] 테이블/그리드 뷰 토글
- [ ] 문서 상세 → 메타데이터 편집 → 저장
- [ ] 문서 삭제

### Phase 2
- [ ] 그래프 노드/엣지 렌더링
- [ ] 줌/패닝, 노드 드래그
- [ ] 토픽별 색상 클러스터링
- [ ] 노드 클릭 → 문서 상세

### Phase 3
- [ ] 검색 입력 → 결과 표시
- [ ] 키워드/시맨틱 모드 전환
- [ ] URL 파라미터 동기화

### Phase 4
- [ ] ADMIN 권한 체크
- [ ] 시스템 상태 + 배치 로그
- [ ] 임베딩 재생성 트리거

### Phase 5
- [ ] Ctrl+K 글로벌 검색
- [ ] 로딩 스켈레톤, 에러 바운더리, 빈 상태 UI
- [ ] 모바일 반응형

---

## 12. 작업 진행 방식

1. **Phase 단위로 순서대로** 진행
2. 한 Phase 안에서 **Step 순서** 준수
3. 각 Step 완료 후 **빌드 확인** (`npm run build`)
4. Phase 완료 시 **체크리스트 검증**
5. 프론트/백 맞물리는 Phase는 **API 스펙 먼저 합의** → 각자 개발 → 연동 테스트

---

*이 문서는 프로젝트 진행에 따라 업데이트됩니다.*
