from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_async_session
from core.fastapi_users_config import current_active_user
from models.user import User
from schemas.source import SourceCreate, SourceResponse
from services.notebook_service import NotebookService
from services.source_service import SourceService

router = APIRouter()


@router.get("", response_model=list[SourceResponse])
async def get_sources_by_notebook(
    notebook_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[SourceResponse]:
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    service = SourceService(session)
    return await service.get_by_notebook_id(notebook_id)


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    data: SourceCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> SourceResponse:
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(data.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    service = SourceService(session)
    return await service.create_source(data)


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> SourceResponse:
    service = SourceService(session)
    source = await service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(source.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    service = SourceService(session)
    source = await service.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(source.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    await service.delete(source)
