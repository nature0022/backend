from pydantic import BaseModel, ConfigDict


class QuizCreate(BaseModel):
    answer: str
    content_id: int


class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    answer: str
    content_id: int
