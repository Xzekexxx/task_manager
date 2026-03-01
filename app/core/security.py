import jwt
import bcrypt
from typing import Annotated, Dict
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.core.config import get_settings
from app.db.database import get_session
from app.db.models import Users
from app.api.schemas.user import UserIn, UserInDB


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

settings = get_settings()

def create_jwt_token(data: Dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCES_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_session)]):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    expire = payload.get("exp")
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истек")
    return payload.get("sub")

async def get_current_user(username: str = Depends(get_user_from_token), db: AsyncSession = Depends(get_session)):
    current_user = (await db.execute(select(Users).where(username == Users.username))).scalar_one_or_none()
    if current_user:
        return UserInDB.model_validate(current_user)

def hash_password(password: str):
    salt = bcrypt.gensalt()
    pwd_bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)

def validate_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode(), hashed_password.encode('utf-8'))


