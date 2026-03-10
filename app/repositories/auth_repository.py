from abc import ABC, abstractmethod
from fastapi import Depends, Response
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.api.schemas.user import UserIn, UserOut, UserInDB
from app.db.database import get_session
from app.db.models import Users
from app.core.security import hash_password, validate_password, create_jwt_token, get_current_user
from app.core.rbac import PremissionChecker

class AuthRep(ABC):
    @abstractmethod
    async def register_user(self, user_data: UserIn):
        pass

    @abstractmethod
    async def login_user(self, response: Response, user_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        pass

    @abstractmethod
    async def about_user(self, current_user: Annotated[UserInDB, Depends(get_current_user)]):
        pass

    @abstractmethod
    async def del_user(self, username: str):
        pass

class SqlAlchemyAuthRep(AuthRep):
    def __init__(self, session: AsyncSession):
        self.db = session

    async def register_user(self, user_data: UserIn):
        get_user_from_db = (await self.db.execute(select(Users).where(user_data.username==Users.username))).scalar_one_or_none()

        if get_user_from_db:
            return {"error": "пользователь с таким именем уже существует"}

        hashed_password = hash_password(user_data.password)

        create_user = Users(
            username = user_data.username,
            email = user_data.email,
            password = hashed_password.decode('utf-8'),
            roles = 'user'
        )

        self.db.add(create_user)
        await self.db.commit()
        await self.db.refresh(create_user)

        return {"message": "You have registered successfully"}
    
    async def login_user(self, response: Response, user_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        get_user_from_db = (await self.db.execute(select(Users).where(user_data.username==Users.username))).scalar_one_or_none()
    
        if not get_user_from_db:
            return {"error": "Пользователь не найден"}
        
        check_password = validate_password(user_data.password, get_user_from_db.password)
        
        if check_password:
            token = create_jwt_token({'sub': user_data.username})
            response.set_cookie(key="users_acces_token", value=token, httponly=True)
            return {"access_token": token, "token_type": "bearer"}
        else:
            return {"error": "Неверный пароль"}

    async def about_user(self, current_user: Annotated[UserInDB, Depends(get_current_user)]):
        return {"username": current_user.username,
            "email": current_user.email,
            "roles": current_user.roles}

    async def del_user(self, username: str):
        user_from_db = (await self.db.execute(select(Users).where(Users.username==username))).scalar_one_or_none()
        await self.db.delete(user_from_db)
        await self.db.commit()
        return {"message": "Пользователь успешно удален"}