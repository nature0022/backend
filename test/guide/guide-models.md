# DAO 구현 플랜: SQLAlchemy ORM + Pydantic Schema

## 개요

ERD(`erd.erd.json`)에 정의된 8개 테이블에 대해 SQLAlchemy ORM 모델과 Pydantic 스키마를 구현합니다.

- **db/ 디렉토리**: 건드리지 않음 (별도 담당자 관리)
- **crud/ 디렉토리**: 사용하지 않음
- **세션 방식**: 모델 자체는 Sync/Async 모두 호환 (SQLAlchemy 2.0 Mapped 스타일)

---

## 1단계: Base 클래스 정의

### `models/base.py` (신규)

```python
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

class Base(DeclarativeBase):
    pass
```

- SQLAlchemy 2.0의 `DeclarativeBase` 사용
- 모든 모델이 이 `Base`를 상속
- DB 담당자가 `db/database.py`에서 `from models.base import Base`로 가져가 `Base.metadata.create_all()` 호출 가능

---

## 2단계: SQLAlchemy ORM 모델 정의

ERD 기반 8개 테이블을 각각 별도 파일로 생성합니다. SQLAlchemy 2.0 `Mapped` + `mapped_column` 스타일을 사용합니다.

### 생성 파일 목록

| 파일 | 테이블 | 주요 컬럼 |
|------|--------|-----------|
| `models/user.py` | user | id, password, email, name, created_at |
| `models/notebook.py` | notebook | id, title, user_id(FK), is_active |
| `models/chat.py` | chat | id, role, message, notebook_id(FK) |
| `models/contents.py` | contents | id, type, notebook_id(FK) |
| `models/directory.py` | directory | id, tags, level, parent_id(FK-self), notebook_id(FK) |
| `models/source.py` | source | id, url, title, summary, notebook_id(FK), directory_id(FK) |
| `models/quiz.py` | quiz | id, answer, content_id(FK) |
| `models/flash_card.py` | flash_card | id, content, content_id(FK) |

### 관계(Relationship) 매핑

```
User ──1:N──> Notebook
Notebook ──1:N──> Chat
Notebook ──1:N──> Contents
Notebook ──1:N──> Directory
Notebook ──1:N──> Source
Directory ──1:N──> Directory (self-referencing, parent_id)
Directory ──1:N──> Source
Contents ──1:N──> Quiz
Contents ──1:N──> FlashCard
```

### 모델 코드 예시 (user.py)

```python
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    notebooks: Mapped[list["Notebook"]] = relationship(back_populates="user")
```

### 모델 코드 예시 (directory.py - self-referencing)

```python
from sqlalchemy import Integer, ForeignKey, ARRAY, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Directory(Base):
    __tablename__ = "directory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("directory.id"), nullable=True)
    notebook_id: Mapped[int] = mapped_column(ForeignKey("notebook.id"), nullable=False)

    parent: Mapped["Directory | None"] = relationship(
        back_populates="children", remote_side="Directory.id"
    )
    children: Mapped[list["Directory"]] = relationship(back_populates="parent")
    notebook: Mapped["Notebook"] = relationship(back_populates="directories")
    sources: Mapped[list["Source"]] = relationship(back_populates="directory")
```

### `models/__init__.py` 업데이트

```python
from models.base import Base
from models.user import User
from models.notebook import Notebook
from models.chat import Chat
from models.contents import Contents
from models.directory import Directory
from models.source import Source
from models.quiz import Quiz
from models.flash_card import FlashCard

__all__ = [
    "Base",
    "User",
    "Notebook",
    "Chat",
    "Contents",
    "Directory",
    "Source",
    "Quiz",
    "FlashCard",
]
```

---

## 3단계: Pydantic Schema 정의

각 테이블에 대해 Request/Response 스키마를 분리합니다.

### 생성 파일 목록

| 파일 | 스키마 |
|------|--------|
| `schemas/user.py` | UserCreate, UserResponse |
| `schemas/notebook.py` | NotebookCreate, NotebookUpdate, NotebookResponse |
| `schemas/chat.py` | ChatCreate, ChatResponse |
| `schemas/contents.py` | ContentsCreate, ContentsResponse |
| `schemas/directory.py` | DirectoryCreate, DirectoryUpdate, DirectoryResponse |
| `schemas/source.py` | SourceCreate, SourceResponse |
| `schemas/quiz.py` | QuizCreate, QuizResponse |
| `schemas/flash_card.py` | FlashCardCreate, FlashCardResponse |

### 스키마 패턴

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    password: str
    email: str
    name: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    created_at: datetime
```

- `ConfigDict(from_attributes=True)`: SQLAlchemy 모델 -> Pydantic 자동 변환 지원
- `UserCreate`에는 `password` 포함, `UserResponse`에는 `password` 제외 (보안)
- `| None`을 사용하여 Optional 표현 (Python 3.10+ 스타일)

### `schemas/__init__.py` 업데이트

모든 스키마를 export합니다.

---

## 4단계: Dependency Injection 연동 가이드

DB 세션은 DB 담당자가 관리하므로, 여기서는 **연동 인터페이스만 문서화**합니다.

### DB 담당자에게 전달할 사항

1. `models/base.py`에서 `Base`를 import하여 `Base.metadata.create_all(engine)` 호출
2. 세션 팩토리 생성 시 모든 모델이 import되어야 함 → `import models` 한 줄이면 충분
3. Async 세션이 필요한 경우 `asyncpg` + `create_async_engine` 사용

### FastAPI Dependency 예시 (참고용)

```python
# db/database.py (DB 담당자 영역)
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# api/endpoints/users.py (사용 예시)
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_session

@router.get("/users/{user_id}")
async def get_user(user_id: int, session: AsyncSession = Depends(get_async_session)):
    ...
```

---

## 작업 순서 요약

1. `models/base.py` 생성 (DeclarativeBase)
2. `models/user.py` 생성
3. `models/notebook.py` 생성
4. `models/chat.py` 생성
5. `models/contents.py` 생성
6. `models/directory.py` 생성
7. `models/source.py` 생성
8. `models/quiz.py` 생성
9. `models/flash_card.py` 생성
10. `models/__init__.py` 업데이트 (전체 모델 export)
11. `schemas/user.py` 생성
12. `schemas/notebook.py` 생성
13. `schemas/chat.py` 생성
14. `schemas/contents.py` 생성
15. `schemas/directory.py` 생성
16. `schemas/source.py` 생성
17. `schemas/quiz.py` 생성
18. `schemas/flash_card.py` 생성
19. `schemas/__init__.py` 업데이트 (전체 스키마 export)

---

## 검증 방법

1. `python -c "from models import Base, User, Notebook, Chat, Contents, Directory, Source, Quiz, FlashCard; print('Models OK')"` - import 성공 확인
2. `python -c "from schemas.user import UserCreate, UserResponse; print('Schemas OK')"` - 스키마 import 확인
3. `ruff check models/ schemas/` - 코드 스타일 검증
4. `Base.metadata.tables.keys()` 로 8개 테이블 등록 확인

---

## 변경되지 않는 파일

- `db/` 디렉토리 전체 (DB 담당자 관리)
- `crud/` 디렉토리 (사용하지 않음)
- `main.py`, `core/`, `api/` (기존 유지)
