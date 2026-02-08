from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Notebook(Base):
    __tablename__ = "notebook"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="notebooks")
    chats: Mapped[list["Chat"]] = relationship(back_populates="notebook")
    contents_list: Mapped[list["Contents"]] = relationship(back_populates="notebook")
    directories: Mapped[list["Directory"]] = relationship(back_populates="notebook")
    sources: Mapped[list["Source"]] = relationship(back_populates="notebook")
