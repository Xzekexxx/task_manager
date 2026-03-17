from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.endpoints.auth import auth
from app.api.endpoints.task import task
from app.core.room_manager import room_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    yield
    await room_manager.close()

app = FastAPI(lifespan=lifespan)

app.include_router(auth)
app.include_router(task)

@app.get('/')
async def hello():
    return 'hello'