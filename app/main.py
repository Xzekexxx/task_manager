from fastapi import FastAPI

from app.api.endpoints.auth import auth

app = FastAPI()

app.include_router(auth)

@app.get('/')
async def hello():
    return 'hello'