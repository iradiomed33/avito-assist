import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from jose import jwt, JWTError

from app.core.config import Settings

STATE_TTL_SECONDS = 10 * 60  # 10 минут


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_oauth_state(settings: Settings, user_id: int, project_id: int) -> str:
    payload = {
        "typ": "avito_oauth_state",
        "sub": str(user_id),
        "project_id": int(project_id),
        "nonce": secrets.token_urlsafe(8),
        "exp": int((_now_utc() + timedelta(seconds=STATE_TTL_SECONDS)).timestamp()),
        "iat": int(_now_utc().timestamp()),
    }
    # Используем тот же секрет, что и JWT (предполагаю, он уже есть в Settings как SECRET_KEY)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_oauth_state(settings: Settings, state: str) -> dict:
    try:
        payload = jwt.decode(state, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError as e:
        raise ValueError("Invalid state") from e

    if payload.get("typ") != "avito_oauth_state":
        raise ValueError("Invalid state type")

    if "project_id" not in payload or "sub" not in payload:
        raise ValueError("Invalid state payload")

    return payload


def build_authorize_url(settings: Settings, state: str) -> str:
    # Avito OAuth endpoint: https://avito.ru/oauth :contentReference[oaicite:5]{index=5}
    params = {
        "response_type": "code",
        "client_id": settings.AVITO_CLIENT_ID,
        "redirect_uri": settings.AVITO_REDIRECT_URI,
        "scope": settings.AVITO_SCOPES,
        "state": state,
    }
    return f"{settings.AVITO_AUTH_URL}?{urlencode(params)}"


async def exchange_code_for_token(settings: Settings, code: str) -> dict:
    # Token endpoint: POST https://api.avito.ru/token :contentReference[oaicite:6]{index=6}
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.AVITO_CLIENT_ID,
        "client_secret": settings.AVITO_CLIENT_SECRET,
        "code": code,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(settings.AVITO_TOKEN_URL, data=data)
        r.raise_for_status()
        return r.json()


async def refresh_token(settings: Settings, refresh_token_value: str) -> dict:
    data = {
        "grant_type": "refresh_token",
        "client_id": settings.AVITO_CLIENT_ID,
        "client_secret": settings.AVITO_CLIENT_SECRET,
        "refresh_token": refresh_token_value,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(settings.AVITO_TOKEN_URL, data=data)
        r.raise_for_status()
        return r.json()


async def fetch_avito_account_self(access_token: str) -> dict:
    # Часто используется /core/v1/accounts/self (информация о пользователе). :contentReference[oaicite:7]{index=7}
    url = "https://api.avito.ru/core/v1/accounts/self"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        return r.json()
