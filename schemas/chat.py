from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    role: str
    message: str
    notebook_id: int


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    message: str
    notebook_id: int
