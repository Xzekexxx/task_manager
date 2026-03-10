from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.api.endpoints.auth import auth
from app.api.endpoints.task import task
from app.core.room_manager import listener

@asynccontextmanager
async def lifespan(app: FastAPI):
    future = asyncio.create_task(listener())
    yield
    future.cancel()
    try:
        await future
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

app.include_router(auth)
app.include_router(task)

@app.get('/')
async def hello():
    return 'hello'