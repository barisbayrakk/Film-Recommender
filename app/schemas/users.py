from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None

class UserUpdate(UserBase):
    password: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_admin: int = 0

    class Config:
        from_attributes = True
