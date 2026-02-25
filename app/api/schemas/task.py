from pydantic import BaseModel, Field
from datetime import date
from enum import Enum

class TaskStatus(Enum):
    CREATED = "created"
    AT_WORK = "at work"
    ON_CHECK = "on check"
    CANCEL = "cancel"
    FINISHED = "finished"

class CreateTask(BaseModel):
    name: str
    description: str | None = None
    created_at: date

class TaskUpdate(BaseModel):
    description: str | None = None
    status: TaskStatus