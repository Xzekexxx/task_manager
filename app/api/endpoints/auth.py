from fastapi import Depends, APIRouter, Response
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.api.schemas.user import UserIn, UserOut, UserInDB
from app.db.database import get_session
from app.db.models import Users
from app.core.security import hash_password, validate_password, create_jwt_token, get_current_user
from app.core.rbac import PremissionChecker
from app.repositories.auth_repository import AuthRep, SqlAlchemyAuthRep

auth = APIRouter(tags=['auth'])

async def auth_rep(db: Annotated[AsyncSession, Depends(get_session)]) -> AuthRep:
    return SqlAlchemyAuthRep(db)

@auth.post('/reg')
async def register_user(user_data: UserIn , rep: Annotated[AuthRep, Depends(auth_rep)]):
    return await rep.register_user(user_data)

@auth.post('/login')
async def login_user(response: Response, user_data: Annotated[OAuth2PasswordRequestForm, Depends()], rep: Annotated[AuthRep, Depends(auth_rep)]):
    return await rep.login_user(response, user_data)
  
@auth.get("/about_user")
@PremissionChecker(["user"])  
async def about_user(rep: Annotated[AuthRep, Depends(auth_rep)], current_user: Annotated[UserInDB, Depends(get_current_user)]):
    return await rep.about_user(current_user)


@auth.delete("/del_user/{username}")
@PremissionChecker(["admin"])  
async def del_user(username: str, rep: Annotated[AuthRep, Depends(auth_rep)], current_user: Annotated[UserInDB, Depends(get_current_user)]):
    return await rep.del_user(username)