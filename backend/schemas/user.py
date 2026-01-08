from pydantic import BaseModel, EmailStr
# from typing import Literal

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
