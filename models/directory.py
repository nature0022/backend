from sqlalchemy import ARRAY, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Directory(Base):
    __tablename__ = "directory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("directory.id"), nullable=True)
    notebook_id: Mapped[int] = mapped_column(ForeignKey("notebook.id"), nullable=False)

    parent: Mapped["Directory | None"] = relationship(back_populates="children", remote_side="Directory.id")
    children: Mapped[list["Directory"]] = relationship(back_populates="parent")
    notebook: Mapped["Notebook"] = relationship(back_populates="directories")
    sources: Mapped[list["Source"]] = relationship(back_populates="directory")
