from datetime import datetime
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    niche: str = Field(default="", max_length=128)
    description: str = Field(default="", max_length=512)

class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=128)
    niche: str | None = Field(default=None, max_length=128)
    description: str | None = Field(default=None, max_length=512)
    status: str | None = Field(default=None, max_length=32)  # active|paused

class ProjectOut(BaseModel):
    id: int
    name: str
    niche: str
    description: str
    status: str
    created_at: datetime
