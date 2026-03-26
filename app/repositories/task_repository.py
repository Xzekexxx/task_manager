from abc import ABC, abstractmethod
from fastapi import Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from sqlalchemy import select
from datetime import datetime
import json

from app.api.schemas.user import UserInDB
from app.db.models import Tasks
from app.core.security import get_current_user
from app.api.schemas.task import TaskOut, TaskCreate, TaskEvent
from app.core.room_manager import redis_client
from app.errors.task import InvalidCredentials, TaskNotFound

class TaskRep(ABC):
    @abstractmethod
    async def create_new_task(self, task: TaskCreate, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)]) -> TaskOut:
        pass
    @abstractmethod
    async def get_tasks(self) -> List[TaskOut]:
        pass
    @abstractmethod
    async def put_task(self, task_id: int, task_data: TaskCreate, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)]) -> TaskOut:
        pass
    @abstractmethod
    async def del_task(self, task_id: int, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)]):
        pass


class SqlAlchemyTaskRep(TaskRep):
    def __init__(self, session: AsyncSession):
        self.db = session

    async def create_new_task(self, task: TaskCreate, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)]) -> TaskOut:
        user = current_user.username
        try:
            new_task = Tasks(
                name=task.name,
                description=task.description,
                created=user,
                created_at=datetime.now(),
                status=task.status
            )
        
            self.db.add(new_task)
            await self.db.commit()
            await self.db.refresh(new_task)

        except:
            raise InvalidCredentials(detail="Invalid credentials")

        message = json.dumps(TaskEvent(event="task create", msg=f'{user} create new task').model_dump())
        await redis_client.publish(room, message)

        return new_task

    async def get_tasks(self) -> List[TaskOut]:
        tasks = (await self.db.execute(select(Tasks))).scalars().all()
        if tasks:
            return tasks
        else:
            raise TaskNotFound(detail="No tasks have been created yet")

    async def put_task(self, task_id: int, task_data: TaskCreate, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)]) -> TaskOut:
        
        cur_task = (await self.db.execute(select(Tasks).where(Tasks.id==task_id))).scalar_one_or_none()

        if not cur_task:
            raise TaskNotFound(detail="task not found")

        user = current_user.username
        try:
            cur_task.name = task_data.name
            cur_task.description = task_data.description
            cur_task.status = task_data.status

            await self.db.commit()
            await self.db.refresh(cur_task)

        except:
            raise InvalidCredentials(detail="Invalid credentials")
        
        await redis_client.publish(room, json.dumps(TaskEvent(event="modified task", msg=f'{user} modified task').model_dump()))

        return cur_task

    async def del_task(self, task_id: int, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)]):
        cur_task = (await self.db.execute(select(Tasks).where(Tasks.id==task_id))).scalar_one_or_none()

        if not cur_task:
            raise TaskNotFound(detail="Task not found")

        user = current_user.username

        await self.db.delete(cur_task)
        await self.db.commit()
        
        await redis_client.publish(room, json.dumps(TaskEvent(event="deleted task", msg=f'{user} deleted the task').model_dump()))

        return {"message": "task deleted successfully"}