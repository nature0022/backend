from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.notebook import Notebook
from schemas.notebook import NotebookCreate, NotebookUpdate
from services.base import BaseService


class NotebookService(BaseService[Notebook]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Notebook, session)

    async def get_by_user_id(self, user_id: int) -> list[Notebook]:
        stmt = select(Notebook).where(Notebook.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_notebook(self, data: NotebookCreate, user_id: int) -> Notebook:
        notebook = Notebook(title=data.title, is_active=data.is_active, user_id=user_id)
        return await self.create(notebook)

    async def update_notebook(self, notebook: Notebook, data: NotebookUpdate) -> Notebook:
        if data.title is not None:
            notebook.title = data.title
        if data.is_active is not None:
            notebook.is_active = data.is_active
        return await self.update(notebook)
