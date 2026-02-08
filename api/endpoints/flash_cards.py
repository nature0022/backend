from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_async_session
from core.fastapi_users_config import current_active_user
from models.user import User
from schemas.flash_card import FlashCardCreate, FlashCardResponse
from services.contents_service import ContentsService
from services.flash_card_service import FlashCardService
from services.notebook_service import NotebookService

router = APIRouter()


@router.get("", response_model=list[FlashCardResponse])
async def get_flash_cards_by_content(
    content_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[FlashCardResponse]:
    contents_service = ContentsService(session)
    contents = await contents_service.get_by_id(content_id)
    if contents is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(contents.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    service = FlashCardService(session)
    return await service.get_by_content_id(content_id)


@router.post("", response_model=FlashCardResponse, status_code=status.HTTP_201_CREATED)
async def create_flash_card(
    data: FlashCardCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> FlashCardResponse:
    contents_service = ContentsService(session)
    contents = await contents_service.get_by_id(data.content_id)
    if contents is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(contents.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    service = FlashCardService(session)
    return await service.create_flash_card(data)


@router.get("/{flash_card_id}", response_model=FlashCardResponse)
async def get_flash_card(
    flash_card_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> FlashCardResponse:
    service = FlashCardService(session)
    flash_card = await service.get_by_id(flash_card_id)
    if flash_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FlashCard not found")
    contents_service = ContentsService(session)
    contents = await contents_service.get_by_id(flash_card.content_id)
    if contents is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FlashCard not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(contents.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FlashCard not found")
    return flash_card


@router.delete("/{flash_card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flash_card(
    flash_card_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    service = FlashCardService(session)
    flash_card = await service.get_by_id(flash_card_id)
    if flash_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FlashCard not found")
    contents_service = ContentsService(session)
    contents = await contents_service.get_by_id(flash_card.content_id)
    if contents is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FlashCard not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(contents.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FlashCard not found")
    await service.delete(flash_card)
