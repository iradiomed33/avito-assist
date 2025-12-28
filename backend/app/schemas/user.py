from datetime import datetime
from pydantic import BaseModel, Field

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    expires_at: datetime | None

class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    role: str = "user"  # admin|user
    is_active: bool = True
    expires_at: datetime | None = None

class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=6, max_length=128)
    role: str | None = None
    is_active: bool | None = None
    expires_at: datetime | None = None
