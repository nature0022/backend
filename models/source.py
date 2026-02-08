from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Source(Base):
    __tablename__ = "source"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    notebook_id: Mapped[int] = mapped_column(ForeignKey("notebook.id"), nullable=False)
    directory_id: Mapped[int | None] = mapped_column(ForeignKey("directory.id"), nullable=True)

    notebook: Mapped["Notebook"] = relationship(back_populates="sources")
    directory: Mapped["Directory | None"] = relationship(back_populates="sources")
