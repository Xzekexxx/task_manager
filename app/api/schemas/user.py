from pydantic import BaseModel, Field, EmailStr

class UserBase(BaseModel):
    username: str = Field(min_length=4, max_length=12)
    email: EmailStr 

class UserIn(UserBase):
    password: str = Field(min_length=6, max_length=12)

class UserOut(UserBase):
    pass

class UserInDB(UserBase):
    hashed_password: str

