from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from app.api.schemas.user import UserInDB
from app.db.database import get_session
from app.core.security import get_current_user
from app.core.rbac import PremissionChecker
from app.api.schemas.task import TaskOut, TaskCreate
from app.core.room_manager import room_manager
from app.repositories.task_repository import SqlAlchemyTaskRep, TaskRep

task = APIRouter(tags=["tasks"])

async def task_rep(db: Annotated[AsyncSession, Depends(get_session)]) -> TaskRep:
    return SqlAlchemyTaskRep(db)


@task.websocket("/ws/{room}")
async def ws(room: str, ws: WebSocket):
    await ws.accept()

    try:
        data = await ws.receive_json()

        token = data.get("token")

        if not token:
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        await ws.send_json({"status": "authorized"})

        if token:
            await room_manager.connect(room, ws)

        while True:
            data = await ws.receive_json()
            if data["type"] == "ping":
                await ws.send_json({"type": "pong"})

    except WebSocketDisconnect:
        await room_manager.disconnect(room, ws)

@task.post("/create_task/{room}", response_model=TaskOut)
@PremissionChecker(["user"])
async def create_new_task(new_task: TaskCreate, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)], rep: Annotated[TaskRep, Depends(task_rep)]):
    return await rep.create_new_task(new_task, room, current_user)

@task.get("/tasks_list", response_model=List[TaskOut])
@PremissionChecker(["user"])
async def get_tasks(current_user: Annotated[UserInDB, Depends(get_current_user)], rep: Annotated[TaskRep, Depends(task_rep)]):
    return await rep.get_tasks()


@task.put("/put_task/{task_id}/{room}", response_model=TaskOut)
@PremissionChecker(["admin"])
async def put_task(task_id: int, task_data: TaskCreate, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)], rep: Annotated[TaskRep, Depends(task_rep)]):
    return await rep.put_task(task_id, task_data, room, current_user)


@task.delete("/del_task/{task_id}/{room}")
@PremissionChecker(["admin"])
async def del_task(task_id: int, room: str, current_user: Annotated[UserInDB, Depends(get_current_user)], rep: Annotated[TaskRep, Depends(task_rep)]):
    return await rep.del_task(task_id, room, current_user)