from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.flash_card import FlashCard
from schemas.flash_card import FlashCardCreate
from services.base import BaseService


class FlashCardService(BaseService[FlashCard]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(FlashCard, session)

    async def get_by_content_id(self, content_id: int) -> list[FlashCard]:
        stmt = select(FlashCard).where(FlashCard.content_id == content_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_flash_card(self, data: FlashCardCreate) -> FlashCard:
        flash_card = FlashCard(content=data.content, content_id=data.content_id)
        return await self.create(flash_card)
