from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    display_name: Optional[constr(max_length=100)] = None


class UserCreate(UserBase):
    password: constr(min_length=8, max_length=72)


class UserRead(UserBase):
    id: int
    is_email_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
