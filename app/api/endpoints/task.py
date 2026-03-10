from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import select
from datetime import datetime
import json
import asyncio

from app.api.schemas.user import UserInDB
from app.db.database import get_session
from app.db.models import Tasks
from app.core.security import get_current_user
from app.core.rbac import PremissionChecker
from app.api.schemas.task import TaskOut, TaskCreate, TaskEvent
from app.core.room_manager import room_manager, redis_client

task = APIRouter(tags=["tasks"])

@task.websocket("/ws/{room}")
async def ws(room: str, ws: WebSocket):
    await ws.accept()

    await room_manager.connect(room, ws)

    try:
        while True:
            data = await ws.receive_json()

            if data["type"] == "ping":
                await ws.send_json({"type": "pong"})

    except WebSocketDisconnect:
        await room_manager.disconnect(room, ws)

@task.post("/create_task/{room}", response_model=TaskOut)
@PremissionChecker(["user"])
async def create_new_task(task: TaskCreate, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_session)]):
    user = current_user.username
    
    new_task = Tasks(
        name=task.name,
        description=task.description,
        created=user,
        created_at=datetime.now(),
        status=task.status
    )
    
    # await redis_client.publish(room, msg=json.dumps(TaskEvent(event="task create", msg=f'{user} create new task').model_dump()))

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    return new_task


@task.get("/tasks_list", response_model=list[TaskOut])
@PremissionChecker(["user"])
async def get_tasks(current_user: Annotated[UserInDB, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_session)]):
    tasks = (await db.execute(select(Tasks))).scalars().all()
    return tasks



@task.put("/put_task/{task_id}/{room}", response_model=TaskOut)
@PremissionChecker(["user"])
async def put_task(task_id: int, task_data: TaskCreate, room: str,current_user: Annotated[UserInDB, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_session)]):
    cur_task = (await db.execute(select(Tasks).where(Tasks.id==task_id))).scalar_one_or_none()

    user = current_user.username

    cur_task.name = task_data.name
    cur_task.description = task_data.description
    cur_task.status = task_data.status

    await redis_client.publish(room, msg=json.dumps(TaskEvent(event="modified task", msg=f'{user} modified task').model_dump()))


    await db.commit()
    await db.refresh(cur_task)

    return cur_task


@task.delete("/del_task/{task_id}/{room}")
@PremissionChecker(["user"])
async def del_task(task_id: int, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_session)]):
    cur_task = (await db.execute(select(Tasks).where(Tasks.id==task_id))).scalar_one_or_none()

    user = current_user.username

    await redis_client.publish(room, msg=json.dumps(TaskEvent(event="deleted task", msg=f'{user} deleted the task').model_dump()))

    await db.delete(cur_task)
    await db.commit()
    
    return {"message": "задача успешно удалена"}