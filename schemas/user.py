from datetime import datetime

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate


class UserRead(BaseUser[int]):
    name: str
    created_at: datetime


class UserCreate(BaseUserCreate):
    name: str


class UserUpdate(BaseUserUpdate):
    name: str | None = None
