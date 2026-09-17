"""TailorResume — Auth Schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
