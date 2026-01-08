from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    """Model for creating a new user"""
    email: EmailStr

class UserResponse(BaseModel):
    """Model for user response"""
    user_id: str
    email: str
    created_at: datetime

class User(BaseModel):
    """Complete user model"""
    user_id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True