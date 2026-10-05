"""Pydantic v2 Schemas for Authentication and User Management."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT Bearer token response."""

    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class TokenPayload(BaseModel):
    """Decoded JWT payload structure."""

    sub: str
    username: str
    role: str
    exp: Optional[int] = None


class UserBase(BaseModel):
    """Base user attributes."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "reviewer"


class UserCreate(UserBase):
    """Schema for registering a new user."""

    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Schema for user authentication request."""

    username: str
    password: str


class UserResponse(UserBase):
    """Public user response schema."""

    id: str
    is_active: bool

    model_config = {"from_attributes": True}
