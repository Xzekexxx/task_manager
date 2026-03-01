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

auth = APIRouter(tags=['auth'])

@auth.post('/reg')
async def register_user(user_data: UserIn, db: Annotated[AsyncSession, Depends(get_session)]):
    get_user_from_db = (await db.execute(select(Users).where(user_data.username==Users.username))).scalar_one_or_none()

    hashed_password = hash_password(user_data.password)

    create_user = Users(
        username = user_data.username,
        email = user_data.email,
        password = hashed_password.decode('utf-8'),
        roles = 'user'
    )

    db.add(create_user)
    await db.commit()
    await db.refresh(create_user)

    return {"message": "You have registered successfully"}

@auth.post('/login')
async def login_user(response: Response, user_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_session)]):
    get_user_from_db = (await db.execute(select(Users).where(user_data.username==Users.username))).scalar_one_or_none()
    
    if not get_user_from_db:
        return {"error": "Пользователь не найден"}
    
    check_password = validate_password(user_data.password, get_user_from_db.password)
    
    if check_password:
        token = create_jwt_token({'sub': user_data.username})
        response.set_cookie(key="users_acces_token", value=token, httponly=True)
        return {"access_token": token, "token_type": "bearer"}
    else:
        return {"error": "Неверный пароль"}
  
@auth.get("/about_user")
@PremissionChecker(["user"])  
async def about_user(current_user: Annotated[UserInDB, Depends(get_current_user)]):
    return {"username": current_user.username,
            "email": current_user.email,
            "roles": current_user.roles}


@auth.delete("/del_user/{username}")
@PremissionChecker(["admin"])  
async def del_user(username: str, db: Annotated[AsyncSession, Depends(get_session)], current_user: Annotated[UserInDB, Depends(get_current_user)]):
    user_from_db = (await db.execute(select(Users).where(Users.username==username))).scalar_one_or_none()
    await db.delete(user_from_db)
    await db.commit()
    return {"message": "Пользователь успешно удален"}