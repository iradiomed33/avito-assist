from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.avito_account import AvitoAccount
from app.services.avito_oauth import (
    verify_oauth_state,
    exchange_code_for_token,
    fetch_avito_account_self,
)

router = APIRouter(tags=["avito-public"])


def _expires_at(expires_in: int | None) -> datetime | None:
    if not expires_in:
        return None
    return datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))


@router.get("/avito/oauth/callback", response_class=HTMLResponse)
async def avito_oauth_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    if error:
        return HTMLResponse(f"<h3>Avito OAuth error</h3><p>{error}</p>", status_code=400)

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code/state")

    # validate state -> получаем user_id и project_id
    try:
        payload = verify_oauth_state(settings, state)
        project_id = int(payload["project_id"])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state")

    # 1) code -> token
    token = await exchange_code_for_token(settings, code)

    access_token = token.get("access_token")
    refresh_token = token.get("refresh_token")
    expires_in = token.get("expires_in")

    if not access_token:
        raise HTTPException(status_code=400, detail="No access_token in response")

    # 2) получаем avito_user_id
    me = await fetch_avito_account_self(access_token)
    # ожидаем что где-то в ответе будет id
    avito_user_id = (
        me.get("id")
        or me.get("data", {}).get("id")
        or me.get("account", {}).get("id")
    )
    if not avito_user_id:
        raise HTTPException(status_code=400, detail="Cannot determine avito_user_id")

    # 3) upsert
    row = (
        db.query(AvitoAccount)
        .filter(AvitoAccount.project_id == project_id, AvitoAccount.avito_user_id == int(avito_user_id))
        .first()
    )

    if not row:
        row = AvitoAccount(project_id=project_id, avito_user_id=int(avito_user_id), access_token=access_token)
        db.add(row)

    row.access_token = access_token
    row.refresh_token = refresh_token
    row.token_expires_at = _expires_at(expires_in)
    row.scopes = settings.AVITO_SCOPES

    db.commit()

    return HTMLResponse(
        "<h3>Avito подключён ✅</h3>"
        "<p>Токены сохранены. Окно можно закрыть.</p>",
        status_code=200,
    )
