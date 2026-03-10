from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from enum import Enum


class TaskCreate(BaseModel):
    name: str = Field(min_length=3, max_length=20)
    description: str | None = None
    status: str

class TaskOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    created: str
    status: str
    created_at: date

    model_config = ConfigDict(from_attributes=True)


class TaskEvent(BaseModel):
    event: str
    msg: str