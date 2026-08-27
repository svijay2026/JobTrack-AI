from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base schema with shared user attributes."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    is_active: Optional[bool] = True


class UserCreate(BaseModel):
    """Schema for registering a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Password (minimum 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")


class UserLogin(BaseModel):
    """Schema for user login using JSON body."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """Schema for returning user data (never includes hashed password)."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
