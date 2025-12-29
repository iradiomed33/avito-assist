from datetime import datetime
from pydantic import BaseModel


class AvitoAccountOut(BaseModel):
    id: int
    project_id: int
    avito_user_id: int
    token_expires_at: datetime | None = None
    scopes: str | None = None

    class Config:
        from_attributes = True


class AvitoOAuthStartOut(BaseModel):
    auth_url: str
