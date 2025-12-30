from datetime import datetime, timedelta, timezone
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings, get_settings
from app.db.session import get_db
from app.models.avito_account import AvitoAccount
from app.services.avito_oauth import (
    verify_oauth_state,
    exchange_code_for_token,
    fetch_avito_account_self,
)

from app.models.avito_webhook_event import AvitoWebhookEvent

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
    settings: settings = Depends(get_settings),
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


@router.post("/webhook")
async def avito_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    t: str | None = None,
    project_id: int | None = None,
    account_id: int | None = None,
    db: Session = Depends(get_db),
):
    # защита от сканеров/ботов
    if settings.AVITO_WEBHOOK_TOKEN:
        if not t or t != settings.AVITO_WEBHOOK_TOKEN:
            raise HTTPException(status_code=401, detail="invalid webhook token")

    raw = await request.body()

    # Avito при регистрации может стучаться с пустым/{} — обязаны быстро ответить 200
    if not raw or raw.strip() in (b"{}", b"[]"):
        return {"ok": True}

    try:
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            payload = {"_raw": payload}
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")

    event = AvitoWebhookEvent(
        project_id=project_id,
        avito_account_id=account_id,
        event_type=str(payload.get("type") or payload.get("event_type") or ""),
        dedup_key=_dedup_key(raw, payload),
        payload_json=json.dumps(payload, ensure_ascii=False),
        status="new",
    )

    try:
        db.add(event)
        db.commit()
        db.refresh(event)
    except IntegrityError:
        db.rollback()
        # дубликат — всё равно 200, чтобы Avito не ретраил
        return {"ok": True, "duplicate": True}

    # ВАЖНО: тяжёлую обработку потом. Сейчас — только сохранили и быстро ответили.
    # background_tasks.add_task(...) подключим на Sprint 2 (обработчик/бот-логика)
    return {"ok": True, "id": event.id}