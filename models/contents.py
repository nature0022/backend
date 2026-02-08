from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Contents(Base):
    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    notebook_id: Mapped[int] = mapped_column(ForeignKey("notebook.id"), nullable=False)

    notebook: Mapped["Notebook"] = relationship(back_populates="contents_list")
    quizzes: Mapped[list["Quiz"]] = relationship(back_populates="contents")
    flash_cards: Mapped[list["FlashCard"]] = relationship(back_populates="contents")
