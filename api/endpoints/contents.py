from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_async_session
from core.fastapi_users_config import current_active_user
from models.user import User
from schemas.contents import ContentsCreate, ContentsResponse
from services.contents_service import ContentsService
from services.notebook_service import NotebookService

router = APIRouter()


@router.get("", response_model=list[ContentsResponse])
async def get_contents_by_notebook(
    notebook_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[ContentsResponse]:
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    service = ContentsService(session)
    return await service.get_by_notebook_id(notebook_id)


@router.post("", response_model=ContentsResponse, status_code=status.HTTP_201_CREATED)
async def create_contents(
    data: ContentsCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> ContentsResponse:
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(data.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    service = ContentsService(session)
    return await service.create_contents(data)


@router.get("/{contents_id}", response_model=ContentsResponse)
async def get_contents(
    contents_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> ContentsResponse:
    service = ContentsService(session)
    contents = await service.get_by_id(contents_id)
    if contents is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(contents.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    return contents


@router.delete("/{contents_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contents(
    contents_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    service = ContentsService(session)
    contents = await service.get_by_id(contents_id)
    if contents is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(contents.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    await service.delete(contents)
