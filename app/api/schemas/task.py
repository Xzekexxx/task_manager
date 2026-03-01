from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from enum import Enum

class TaskStatus(str, Enum):
    CREATED = "created"
    AT_WORK = "at work"
    ON_CHECK = "on check"
    CANCEL = "cancel"
    FINISHED = "finished"

class TaskCreate(BaseModel):
    name: str = Field(min_length=3, max_length=20)
    description: str | None = None
    status: TaskStatus

class TaskOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    created: str
    status: TaskStatus
    created_at: date

    model_config = ConfigDict(from_attributes=True)