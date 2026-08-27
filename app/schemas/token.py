from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Schema for returning access token upon successful login."""
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class TokenPayload(BaseModel):
    """Schema representing decoded JWT payload."""
    sub: Optional[str] = None
    exp: Optional[int] = None
