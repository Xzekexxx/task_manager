from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Users(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] 
    email: Mapped[str]
    password: Mapped[str]