# 작업 히스토리: Models → Schemas → Services → Endpoints 구현

## 작업일: 2026-02-09

---

## Phase 0: 사전 준비

### 패키지 설치

```bash
uv add "fastapi-users[sqlalchemy]" asyncpg
```

- `fastapi-users-db-sqlalchemy==7.0.0` 설치
- `asyncpg==0.31.0` 설치

### core/config.py 수정

- `database_url` 필드 추가 (기본값: `postgresql+asyncpg://localhost/test_auth`)
- `jwt_lifetime_seconds` 필드 추가 (기본값: 3600)

### core/security.py 교체

- 기존 passlib 기반 코드 제거 (passlib 미설치 상태였음)
- fastapi-users `AuthenticationBackend` (JWT + BearerTransport)으로 교체

---

## Phase 1: Models (SQLAlchemy 2.0 Mapped 스타일)

### 생성 파일

| 파일 | 설명 |
|------|------|
| `models/base.py` | DeclarativeBase 정의 |
| `models/user.py` | User 모델 - SQLAlchemyBaseUserTable[int] + Base 다중 상속 |
| `models/notebook.py` | Notebook 모델 - user_id FK |
| `models/chat.py` | Chat 모델 - notebook_id FK |
| `models/contents.py` | Contents 모델 - notebook_id FK |
| `models/directory.py` | Directory 모델 - self-referencing parent_id, notebook_id FK |
| `models/source.py` | Source 모델 - notebook_id, directory_id FK |
| `models/quiz.py` | Quiz 모델 - content_id FK |
| `models/flash_card.py` | FlashCard 모델 - content_id FK |
| `models/__init__.py` | 전체 모델 export |

### 주요 결정사항

- User 모델: `SQLAlchemyBaseUserTable[int]` 상속으로 fastapi-users 통합
  - email, hashed_password, is_active, is_superuser, is_verified는 fastapi-users 제공
  - name, created_at 추가
- 모든 테이블 PK: Integer + autoincrement
- Directory.tags: PostgreSQL ARRAY(Text) 사용
- FlashCard과 Quiz의 relationship은 `contents`로 명명 (Contents 모델 참조)

---

## Phase 2: Schemas (Pydantic v2)

### 생성 파일

| 파일 | 스키마 |
|------|--------|
| `schemas/user.py` | UserRead(BaseUser[int]), UserCreate(BaseUserCreate), UserUpdate(BaseUserUpdate) |
| `schemas/notebook.py` | NotebookCreate, NotebookUpdate, NotebookResponse |
| `schemas/chat.py` | ChatCreate, ChatResponse |
| `schemas/contents.py` | ContentsCreate, ContentsResponse |
| `schemas/directory.py` | DirectoryCreate, DirectoryUpdate, DirectoryResponse |
| `schemas/source.py` | SourceCreate, SourceResponse |
| `schemas/quiz.py` | QuizCreate, QuizResponse |
| `schemas/flash_card.py` | FlashCardCreate, FlashCardResponse |
| `schemas/__init__.py` | 전체 스키마 export |

### 주요 결정사항

- User 스키마: fastapi-users의 BaseUser/BaseUserCreate/BaseUserUpdate 확장
- Response 스키마: `ConfigDict(from_attributes=True)` 적용
- Optional 표현: `| None` 사용 (Python 3.10+ 스타일)

---

## Phase 3: fastapi-users 연결

### 생성 파일

| 파일 | 설명 |
|------|------|
| `core/deps.py` | create_async_engine, async_sessionmaker, get_async_session, get_user_db |
| `core/user_manager.py` | UserManager (IntegerIDMixin + BaseUserManager[User, int]) |
| `core/fastapi_users_config.py` | FastAPIUsers[User, int] 인스턴스, current_active_user |

### 주요 결정사항

- db/ 디렉토리 미사용 → core/deps.py에서 임시 엔진/세션 관리
- JWT 인증 전략 (Bearer transport + JWT strategy)
- UserManager 콜백: on_after_register, on_after_forgot_password, on_after_request_verify

---

## Phase 4: Services

### 생성 파일

| 파일 | 설명 |
|------|------|
| `services/base.py` | Generic BaseService[ModelType] - get_by_id, get_all, create, update, delete |
| `services/notebook_service.py` | NotebookService - get_by_user_id, create_notebook, update_notebook |
| `services/chat_service.py` | ChatService - get_by_notebook_id, create_chat |
| `services/contents_service.py` | ContentsService - get_by_notebook_id, create_contents |
| `services/directory_service.py` | DirectoryService - get_by_notebook_id, get_children, create/update |
| `services/source_service.py` | SourceService - get_by_notebook_id, create_source |
| `services/quiz_service.py` | QuizService - get_by_content_id, create_quiz |
| `services/flash_card_service.py` | FlashCardService - get_by_content_id, create_flash_card |
| `services/__init__.py` | 전체 서비스 export |

### 주요 결정사항

- crud/ 디렉토리 미사용 → services에서 DB 조작 + 비즈니스 로직 통합
- User 서비스는 없음 (fastapi-users UserManager가 처리)
- Generic BaseService로 공통 CRUD 추상화

---

## Phase 5: Endpoints

### 생성 파일

| 파일 | Prefix | 기능 |
|------|--------|------|
| `api/endpoints/users.py` | /auth, /users | fastapi-users 내장 라우터 (login, register, verify, reset, users) |
| `api/endpoints/notebooks.py` | /notebooks | GET(목록), POST, GET(단건), PATCH, DELETE |
| `api/endpoints/chats.py` | /chats | GET(notebook별), POST, GET(단건), DELETE |
| `api/endpoints/contents.py` | /contents | GET(notebook별), POST, GET(단건), DELETE |
| `api/endpoints/directories.py` | /directories | GET(notebook별), POST, GET(단건), PATCH, DELETE, GET(children) |
| `api/endpoints/sources.py` | /sources | GET(notebook별), POST, GET(단건), DELETE |
| `api/endpoints/quizzes.py` | /quizzes | GET(content별), POST, GET(단건), DELETE |
| `api/endpoints/flash_cards.py` | /flash-cards | GET(content별), POST, GET(단건), DELETE |

### 수정 파일

- `api/route.py` — 전체 라우터 통합
- `main.py` — lifespan 이벤트 추가 (Base.metadata.create_all)

### 주요 결정사항

- 모든 엔드포인트: `current_active_user` 의존성으로 인증 보호
- 소유권 검증: notebook.user_id == user.id 체크
- 하위 리소스(chat, contents 등): notebook 소유권을 통해 간접 검증

---

## 기타 수정

- `ruff.toml` — per-file-ignores 추가 (B008 for endpoints, F821 for models)
- `api/endpoints/health.py` — `timezone.utc` → `UTC` 별칭 사용 (UP017)

---

## 건드리지 않은 디렉토리

- `db/` — 별도 담당자 관리
- `crud/` — 사용하지 않음

---

## 검증 결과

- `ruff check .` — All checks passed
- `ruff format --check .` — 50 files already formatted
