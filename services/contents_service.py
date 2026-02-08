from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.contents import Contents
from schemas.contents import ContentsCreate
from services.base import BaseService


class ContentsService(BaseService[Contents]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Contents, session)

    async def get_by_notebook_id(self, notebook_id: int) -> list[Contents]:
        stmt = select(Contents).where(Contents.notebook_id == notebook_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_contents(self, data: ContentsCreate) -> Contents:
        contents = Contents(type=data.type, notebook_id=data.notebook_id)
        return await self.create(contents)
