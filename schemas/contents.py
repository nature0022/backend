from pydantic import BaseModel, ConfigDict


class ContentsCreate(BaseModel):
    type: str
    notebook_id: int


class ContentsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    notebook_id: int
