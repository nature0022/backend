from pydantic import BaseModel, ConfigDict


class FlashCardCreate(BaseModel):
    content: str | None = None
    content_id: int


class FlashCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str | None
    content_id: int
