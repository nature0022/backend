from pydantic import BaseModel, ConfigDict


class NotebookCreate(BaseModel):
    title: str
    is_active: bool = True


class NotebookUpdate(BaseModel):
    title: str | None = None
    is_active: bool | None = None


class NotebookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    is_active: bool
    user_id: int
