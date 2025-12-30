import json
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.avito_account import AvitoAccount  # поправь импорт под свой проект
from app.models.avito_chat_state import AvitoChatState
from app.services.avito_messenger_client import AvitoMessengerClient


def _find_chat_id(payload: Any) -> Optional[str]:
    # максимально “пуленепробиваемо”: ищем chat_id рекурсивно
    if isinstance(payload, dict):
        for k in ("chat_id", "chatId"):
            if k in payload and isinstance(payload[k], str):
                return payload[k]
        # часто бывает {"chat": {"id": "..."}}
        if "chat" in payload and isinstance(payload["chat"], dict):
            v = payload["chat"].get("id")
            if isinstance(v, str):
                return v

        for v in payload.values():
            cid = _find_chat_id(v)
            if cid:
                return cid

    if isinstance(payload, list):
        for v in payload:
            cid = _find_chat_id(v)
            if cid:
                return cid

    return None


def _extract_last_message(messages_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # разные ответы у разных версий/форматов, пытаемся угадать
    for path in (
        ("messages",),
        ("data", "messages"),
        ("result", "messages"),
        ("items",),
        ("data", "items"),
    ):
        cur: Any = messages_json
        ok = True
        for p in path:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                ok = False
                break
        if ok and isinstance(cur, list) and cur:
            return cur[0]
    return None


def _is_inbound(message: Dict[str, Any], our_user_id: int) -> Tuple[bool, Optional[str]]:
    """
    Возвращает (is_inbound, message_id)
    inbound = не от нашего аккаунта (чтобы не словить петлю автоответов)
    """
    msg_id = None
    for k in ("id", "message_id", "messageId"):
        if isinstance(message.get(k), str):
            msg_id = message[k]
            break

    # автор может называться по-разному
    author = None
    for k in ("author_id", "authorId", "from_id", "fromId"):
        if message.get(k) is not None:
            author = message.get(k)
            break
    if author is None and isinstance(message.get("from"), dict):
        author = message["from"].get("id")

    # если не смогли определить автора — считаем inbound (чтобы не пропускать),
    # но dedup всё равно спасёт от шторма
    if author is None:
        return True, msg_id

    try:
        return int(author) != int(our_user_id), msg_id
    except Exception:
        return True, msg_id


def process_incoming_webhook(account_id: int, payload: Dict[str, Any]) -> None:
    if not settings.AVITO_AUTOREPLY_ENABLED:
        return

    chat_id = _find_chat_id(payload)
    if not chat_id:
        return

    db = SessionLocal()
    try:
        account = db.query(AvitoAccount).filter(AvitoAccount.id == account_id).one_or_none()
        if not account or not account.user_id or not account.access_token:
            return

        client = AvitoMessengerClient(access_token=account.access_token)

        # 1) достаём последнее сообщение чата
        msgs = client.get_messages_v3(user_id=account.user_id, chat_id=chat_id, limit=5, offset=0)
        last = _extract_last_message(msgs)
        if not last:
            return

        inbound, msg_id = _is_inbound(last, our_user_id=account.user_id)

        if settings.AVITO_AUTOREPLY_ONLY_IF_INBOUND and not inbound:
            return

        # 2) dedup по message_id
        state = (
            db.query(AvitoChatState)
            .filter(AvitoChatState.avito_account_id == account_id, AvitoChatState.chat_id == chat_id)
            .one_or_none()
        )
        if not state:
            state = AvitoChatState(avito_account_id=account_id, chat_id=chat_id, last_inbound_message_id=None)
            db.add(state)
            db.commit()
            db.refresh(state)

        if msg_id and state.last_inbound_message_id == msg_id:
            return

        # 3) отправляем автоответ
        client.send_text_message_v1(user_id=account.user_id, chat_id=chat_id, text=settings.AVITO_AUTOREPLY_TEXT)

        # 4) фиксируем последнее обработанное
        if msg_id:
            state.last_inbound_message_id = msg_id
            db.add(state)
            db.commit()

    finally:
        db.close()
