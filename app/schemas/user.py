from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    role: Optional[str] = "viewer"
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserRead(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
