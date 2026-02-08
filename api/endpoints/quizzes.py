from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_async_session
from core.fastapi_users_config import current_active_user
from models.user import User
from schemas.quiz import QuizCreate, QuizResponse
from services.contents_service import ContentsService
from services.notebook_service import NotebookService
from services.quiz_service import QuizService

router = APIRouter()


@router.get("", response_model=list[QuizResponse])
async def get_quizzes_by_content(
    content_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[QuizResponse]:
    contents_service = ContentsService(session)
    contents = await contents_service.get_by_id(content_id)
    if contents is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(contents.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    service = QuizService(session)
    return await service.get_by_content_id(content_id)


@router.post("", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    data: QuizCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> QuizResponse:
    contents_service = ContentsService(session)
    contents = await contents_service.get_by_id(data.content_id)
    if contents is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(contents.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contents not found")
    service = QuizService(session)
    return await service.create_quiz(data)


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> QuizResponse:
    service = QuizService(session)
    quiz = await service.get_by_id(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    contents_service = ContentsService(session)
    contents = await contents_service.get_by_id(quiz.content_id)
    if contents is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(contents.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    return quiz


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    service = QuizService(session)
    quiz = await service.get_by_id(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    contents_service = ContentsService(session)
    contents = await contents_service.get_by_id(quiz.content_id)
    if contents is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    notebook_service = NotebookService(session)
    notebook = await notebook_service.get_by_id(contents.notebook_id)
    if notebook is None or notebook.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    await service.delete(quiz)
