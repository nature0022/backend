from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_async_session
from core.fastapi_users_config import current_active_user
from models.user import User
from schemas.chat import ChatCreate, ChatResponse
from services.chat_service import ChatService
from services.notebook_service import NotebookService

router = APIRouter()


@router.get("", response_model=list[ChatResponse])
async def get_chats_by_notebook(
    notebook_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[ChatResponse]:
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    service = ChatService(session)
    return await service.get_by_notebook_id(notebook_id)


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    data: ChatCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> ChatResponse:
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(data.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    service = ChatService(session)
    return await service.create_chat(data)


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> ChatResponse:
    service = ChatService(session)
    chat = await service.get_by_id(chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(chat.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    service = ChatService(session)
    chat = await service.get_by_id(chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(chat.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    await service.delete(chat)
