from pydantic import BaseModel, ConfigDict


class SourceCreate(BaseModel):
    url: str | None = None
    title: str | None = None
    summary: str | None = None
    notebook_id: int
    directory_id: int | None = None


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str | None
    title: str | None
    summary: str | None
    notebook_id: int
    directory_id: int | None
