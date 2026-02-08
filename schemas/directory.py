from pydantic import BaseModel, ConfigDict


class DirectoryCreate(BaseModel):
    tags: list[str] | None = None
    level: int | None = None
    parent_id: int | None = None
    notebook_id: int


class DirectoryUpdate(BaseModel):
    tags: list[str] | None = None
    level: int | None = None
    parent_id: int | None = None


class DirectoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tags: list[str] | None
    level: int | None
    parent_id: int | None
    notebook_id: int
