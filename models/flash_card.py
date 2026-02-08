from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class FlashCard(Base):
    __tablename__ = "flash_card"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id"), nullable=False)

    contents: Mapped["Contents"] = relationship(back_populates="flash_cards")
