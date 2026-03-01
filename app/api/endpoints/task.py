from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import select
from datetime import datetime

from app.api.schemas.user import UserIn, UserOut, UserInDB
from app.db.database import get_session
from app.db.models import Users, Tasks
from app.core.security import get_current_user
from app.core.rbac import PremissionChecker
from app.api.schemas.task import TaskOut, TaskCreate, TaskStatus

task = APIRouter(tags=["tasks"])

@task.post("/create_task/{task_name}/{description}/{task_status}", response_model=TaskOut)
async def create_new_task(task_name: str, description: str, task_status: TaskStatus,current_user: Annotated[UserInDB, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_session)]):
    user = current_user.username
    
    task = Tasks(
        name=task_name,
        description=description,
        created=user,
        created_at=datetime.now(),
        status=task_status.value
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return task

@task.get("/tasks_list", response_model=list[TaskOut])
async def get_tasks(current_user: Annotated[UserInDB, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_session)]):
    tasks = (await db.execute(select(Tasks))).scalars().all()
    return tasks

@task.put("/put_task/{task_id}", response_model=TaskOut)
async def put_task(task_id: int, task_data: TaskCreate, current_user: Annotated[UserInDB, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_session)]):
    cur_task = (await db.execute(select(Tasks).where(Tasks.id==task_id))).scalar_one_or_none()

    cur_task.name = task_data.name
    cur_task.description = task_data.description
    cur_task.status = task_data.status

    await db.commit()
    await db.refresh(cur_task)

    return cur_task

@task.delete("/del_task/{task_id}")
async def del_task(task_id: int, current_user: Annotated[UserInDB, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_session)]):
    cur_task = (await db.execute(select(Tasks).where(Tasks.id==task_id))).scalar_one_or_none()

    await db.delete(cur_task)
    await db.commit()
    
    return {"message": "задача успешно удалена"}