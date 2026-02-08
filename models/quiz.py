from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Quiz(Base):
    __tablename__ = "quiz"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    answer: Mapped[str] = mapped_column(String(500), nullable=False)
    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id"), nullable=False)

    contents: Mapped["Contents"] = relationship(back_populates="quizzes")
