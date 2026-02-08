from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.quiz import Quiz
from schemas.quiz import QuizCreate
from services.base import BaseService


class QuizService(BaseService[Quiz]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Quiz, session)

    async def get_by_content_id(self, content_id: int) -> list[Quiz]:
        stmt = select(Quiz).where(Quiz.content_id == content_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_quiz(self, data: QuizCreate) -> Quiz:
        quiz = Quiz(answer=data.answer, content_id=data.content_id)
        return await self.create(quiz)
