구현 플랜: Models → Schemas → Services → Endpoints (fastapi-users 통합)
Context
ERD에 정의된 8개 테이블(User, Notebook, Chat, Contents, Directory, Source, Quiz, FlashCard)에 대해
fastapi-users 라이브러리를 활용한 전체 REST API 백엔드를 구현합니다.

db/ 건드리지 않음 → core/deps.py에 임시 세션 관리
crud/ 사용하지 않음 → services/에서 DB 조작 + 비즈니스 로직 통합
core/security.py의 passlib은 미설치 상태 → fastapi-users의 JWT 인증으로 교체
Phase 0: 사전 준비
0-1. 패키지 설치

uv add "fastapi-users[sqlalchemy]" asyncpg
fastapi-users-db-sqlalchemy: SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase 제공
asyncpg: PostgreSQL async 드라이버
0-2. core/config.py 수정
database_url 추가 (기본값: sqlite+aiosqlite:///./test.db)
jwt_lifetime_seconds 추가 (기본값: 3600)
0-3. core/security.py 교체
passlib 코드 제거 → fastapi-users AuthenticationBackend (JWT + BearerTransport)으로 교체
Phase 1: Models (SQLAlchemy 2.0 Mapped 스타일)
1-1. models/base.py — DeclarativeBase
1-2. models/user.py — 핵심: SQLAlchemyBaseUserTable[int] + Base 다중 상속
fastapi-users 제공: email, hashed_password, is_active, is_superuser, is_verified
ERD 추가 필드: name(String), created_at(DateTime, server_default=func.now())
정수 PK (autoincrement)
1-3~1-9. 나머지 7개 모델
파일	테이블	FK
models/notebook.py	notebook	user_id → user
models/chat.py	chat	notebook_id → notebook
models/contents.py	contents	notebook_id → notebook
models/directory.py	directory	parent_id → directory(self), notebook_id → notebook
models/source.py	source	notebook_id → notebook, directory_id → directory
models/quiz.py	quiz	content_id → contents
models/flash_card.py	flash_card	content_id → contents
1-10. models/__init__.py — 전체 모델 export
Phase 2: Schemas (Pydantic v2)
2-1. schemas/user.py — fastapi-users 스키마 확장
UserRead(BaseUser[int]) + name, created_at
UserCreate(BaseUserCreate) + name
UserUpdate(BaseUserUpdate) + name (optional)
2-2~2-8. 나머지 7개 스키마
각 엔티티별 Create / Update(필요시) / Response 분리
ConfigDict(from_attributes=True) 적용
2-9. schemas/__init__.py — 전체 스키마 export
Phase 3: fastapi-users 연결 (core/ 신규 파일 3개)
3-1. core/deps.py — DB 세션 + fastapi-users 어댑터
create_async_engine + async_sessionmaker (db/ 대신 임시 관리)
get_async_session() 제너레이터
get_user_db() → SQLAlchemyUserDatabase(session, User)
3-2. core/user_manager.py — UserManager
IntegerIDMixin + BaseUserManager[User, int]
on_after_register, on_after_forgot_password 콜백
3-3. core/fastapi_users_config.py — FastAPIUsers 인스턴스
FastAPIUsers[User, int] 생성
current_active_user 의존성 export
Phase 4: Services (비즈니스 로직 + DB 조작)
4-1. services/base.py — Generic BaseService[ModelType]
get_by_id, get_all, create, update, delete 공통 메서드
4-2~4-8. 도메인별 서비스 (7개, User는 fastapi-users가 처리)
파일	서비스	추가 메서드
services/notebook_service.py	NotebookService	get_by_user_id, create_notebook, update_notebook
services/chat_service.py	ChatService	get_by_notebook_id
services/contents_service.py	ContentsService	get_by_notebook_id
services/directory_service.py	DirectoryService	get_by_notebook_id, get_children
services/source_service.py	SourceService	get_by_notebook_id
services/quiz_service.py	QuizService	get_by_content_id
services/flash_card_service.py	FlashCardService	get_by_content_id
4-9. services/__init__.py — 전체 서비스 export
Phase 5: Endpoints (HTTP 요청/응답)
5-1. api/endpoints/users.py — fastapi-users 내장 라우터 연결
/auth/login, /auth/register, /auth/verify, /auth/forgot-password
/users/me, /users/{id}
5-2~5-8. 도메인별 엔드포인트 (7개)
각 엔드포인트: GET(목록), POST(생성), GET(단건), PATCH(수정), DELETE(삭제)
current_active_user 의존성으로 인증 보호
소유권 검증 (notebook.user_id == user.id)
파일	Prefix	Tag
api/endpoints/notebooks.py	/notebooks	notebooks
api/endpoints/chats.py	/chats	chats
api/endpoints/contents.py	/contents	contents
api/endpoints/directories.py	/directories	directories
api/endpoints/sources.py	/sources	sources
api/endpoints/quizzes.py	/quizzes	quizzes
api/endpoints/flash_cards.py	/flash-cards	flash-cards
5-9. api/route.py 수정 — 전체 라우터 통합
5-10. main.py 수정 — lifespan 이벤트로 테이블 자동 생성
파일 변경 요약
신규 파일 (28개)
models/: base.py + 8개 모델 파일
schemas/: 8개 스키마 파일
core/: deps.py, user_manager.py, fastapi_users_config.py
services/: base.py + 7개 서비스 파일
api/endpoints/: users.py + 7개 엔드포인트 파일
수정 파일 (6개)
core/config.py — database_url, jwt_lifetime_seconds 추가
core/security.py — passlib → JWT AuthenticationBackend
models/__init__.py — 전체 모델 export
schemas/__init__.py — 전체 스키마 export
api/route.py — 전체 라우터 등록
main.py — lifespan 추가 (Base.metadata.create_all)
건드리지 않는 디렉토리
db/ — 별도 담당자 관리
crud/ — 사용하지 않음
검증
ruff check . && ruff format --check . — 코드 스타일 확인
uvicorn main:app --reload — 서버 기동 확인
/docs Swagger UI에서 전체 엔드포인트 확인
test/guide/history-dto.md에 작업 히스토리 기록