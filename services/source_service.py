from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.source import Source
from schemas.source import SourceCreate
from services.base import BaseService


class SourceService(BaseService[Source]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Source, session)

    async def get_by_notebook_id(self, notebook_id: int) -> list[Source]:
        stmt = select(Source).where(Source.notebook_id == notebook_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_source(self, data: SourceCreate) -> Source:
        source = Source(
            url=data.url,
            title=data.title,
            summary=data.summary,
            notebook_id=data.notebook_id,
            directory_id=data.directory_id,
        )
        return await self.create(source)
