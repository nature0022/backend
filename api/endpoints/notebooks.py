from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_async_session
from core.fastapi_users_config import current_active_user
from models.user import User
from schemas.notebook import NotebookCreate, NotebookResponse, NotebookUpdate
from services.notebook_service import NotebookService

router = APIRouter()


@router.get("", response_model=list[NotebookResponse])
async def get_notebooks(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[NotebookResponse]:
    service = NotebookService(session)
    return await service.get_by_user_id(user.id)


@router.post("", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    data: NotebookCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotebookResponse:
    service = NotebookService(session)
    return await service.create_notebook(data, user.id)


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotebookResponse:
    service = NotebookService(session)
    notebook = await service.get_by_id(notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    return notebook


@router.patch("/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: int,
    data: NotebookUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> NotebookResponse:
    service = NotebookService(session)
    notebook = await service.get_by_id(notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    return await service.update_notebook(notebook, data)


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    service = NotebookService(session)
    notebook = await service.get_by_id(notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    await service.delete(notebook)
