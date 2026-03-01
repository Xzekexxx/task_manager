from fastapi import FastAPI

from app.api.endpoints.auth import auth
from app.api.endpoints.task import task

app = FastAPI()

app.include_router(auth)
app.include_router(task)

@app.get('/')
async def hello():
    return 'hello'