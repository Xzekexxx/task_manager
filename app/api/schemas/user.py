from pydantic import BaseModel, Field, EmailStr, ConfigDict

class UserBase(BaseModel):
    username: str = Field(min_length=4, max_length=12)
    email: EmailStr 

    model_config = ConfigDict(from_attributes=True)

class UserIn(UserBase):
    password: str = Field(min_length=6, max_length=12)
    
    model_config = ConfigDict(from_attributes=True)

class UserOut(UserBase):
    pass

class UserInDB(UserBase):
    password: str

    model_config = ConfigDict(from_attributes=True)