from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.directory import Directory
from schemas.directory import DirectoryCreate, DirectoryUpdate
from services.base import BaseService


class DirectoryService(BaseService[Directory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Directory, session)

    async def get_by_notebook_id(self, notebook_id: int) -> list[Directory]:
        stmt = select(Directory).where(Directory.notebook_id == notebook_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_children(self, parent_id: int) -> list[Directory]:
        stmt = select(Directory).where(Directory.parent_id == parent_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_directory(self, data: DirectoryCreate) -> Directory:
        directory = Directory(tags=data.tags, level=data.level, parent_id=data.parent_id, notebook_id=data.notebook_id)
        return await self.create(directory)

    async def update_directory(self, directory: Directory, data: DirectoryUpdate) -> Directory:
        if data.tags is not None:
            directory.tags = data.tags
        if data.level is not None:
            directory.level = data.level
        if data.parent_id is not None:
            directory.parent_id = data.parent_id
        return await self.update(directory)
