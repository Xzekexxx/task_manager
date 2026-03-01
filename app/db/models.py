from sqlalchemy.orm import Mapped, mapped_column
from typing import List
from sqlalchemy import JSON
from app.db.base import Base

class Users(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] 
    email: Mapped[str]
    password: Mapped[str]
    roles: Mapped[List[str]] = mapped_column(JSON ,default=list)