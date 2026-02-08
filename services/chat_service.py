from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.chat import Chat
from schemas.chat import ChatCreate
from services.base import BaseService


class ChatService(BaseService[Chat]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Chat, session)

    async def get_by_notebook_id(self, notebook_id: int) -> list[Chat]:
        stmt = select(Chat).where(Chat.notebook_id == notebook_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_chat(self, data: ChatCreate) -> Chat:
        chat = Chat(role=data.role, message=data.message, notebook_id=data.notebook_id)
        return await self.create(chat)
