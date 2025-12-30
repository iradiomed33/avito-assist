from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.services.avito_messenger_client import AvitoMessengerClient

# ВАЖНО: тут я предполагаю, что у тебя есть модель AvitoAccount в БД со столбцами:
# id, user_id, access_token
# Если названия отличаются — подправишь 3 строки.
from app.models.avito_account import AvitoAccount  # <-- если файл/класс иначе - скажешь, поправлю


router = APIRouter(prefix="/avito/webhooks", tags=["avito-webhooks"])


@router.post("/subscribe")
def subscribe(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(AvitoAccount).filter(AvitoAccount.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="avito account not found")
    if not acc.access_token:
        raise HTTPException(status_code=400, detail="account has no access_token")

    webhook_url = (
        f"{settings.PUBLIC_BASE_URL}/avito/webhook"
        f"?t={settings.AVITO_WEBHOOK_TOKEN}"
        f"&account_id={account_id}"
    )

    client = AvitoMessengerClient(access_token=acc.access_token)
    resp = client.subscribe_webhook_v3(webhook_url)
    return {"ok": True, "webhook_url": webhook_url, "avito_response": resp}
