from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_async_session
from core.fastapi_users_config import current_active_user
from models.user import User
from schemas.directory import DirectoryCreate, DirectoryResponse, DirectoryUpdate
from services.directory_service import DirectoryService
from services.notebook_service import NotebookService

router = APIRouter()


@router.get("", response_model=list[DirectoryResponse])
async def get_directories_by_notebook(
    notebook_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[DirectoryResponse]:
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    service = DirectoryService(session)
    return await service.get_by_notebook_id(notebook_id)


@router.post("", response_model=DirectoryResponse, status_code=status.HTTP_201_CREATED)
async def create_directory(
    data: DirectoryCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> DirectoryResponse:
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(data.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    service = DirectoryService(session)
    return await service.create_directory(data)


@router.get("/{directory_id}", response_model=DirectoryResponse)
async def get_directory(
    directory_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> DirectoryResponse:
    service = DirectoryService(session)
    directory = await service.get_by_id(directory_id)
    if directory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(directory.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")
    return directory


@router.patch("/{directory_id}", response_model=DirectoryResponse)
async def update_directory(
    directory_id: int,
    data: DirectoryUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> DirectoryResponse:
    service = DirectoryService(session)
    directory = await service.get_by_id(directory_id)
    if directory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(directory.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")
    return await service.update_directory(directory, data)


@router.get("/{directory_id}/children", response_model=list[DirectoryResponse])
async def get_directory_children(
    directory_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[DirectoryResponse]:
    service = DirectoryService(session)
    directory = await service.get_by_id(directory_id)
    if directory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(directory.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")
    return await service.get_children(directory_id)


@router.delete("/{directory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_directory(
    directory_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    service = DirectoryService(session)
    directory = await service.get_by_id(directory_id)
    if directory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(directory.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")
    await service.delete(directory)
