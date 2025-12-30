import httpx
from typing import Any, Dict, Optional



class AvitoMessengerClient:
    def __init__(self, access_token: str):
        self.base_url = "https://api.avito.ru"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def subscribe_webhook_v3(self, url: str) -> dict:
        # по meassege_new.pdf: POST /messenger/v3/webhook { "url": "..." }
        endpoint = f"{self.base_url}/messenger/v3/webhook"
        with httpx.Client(timeout=10.0) as client:
            r = client.post(endpoint, headers=self.headers, json={"url": url})
            r.raise_for_status()
            return r.json()

    def get_messages_v3(self, user_id: int, chat_id: str, limit: int = 10, offset: int = 0) -> dict:
        """
        GET /messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/
        """
        endpoint = f"{self.base_url}/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/"
        params = {"limit": limit, "offset": offset}
        with httpx.Client(timeout=10.0) as client:
            r = client.get(endpoint, headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()

    def send_text_message_v1(self, user_id: int, chat_id: str, text: str) -> dict:
        """
        POST /messenger/v1/accounts/{user_id}/chats/{chat_id}/messages
        payload: {"type":"text","message":{"text":"..."}}
        """
        endpoint = f"{self.base_url}/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages"
        payload = {"type": "text", "message": {"text": text}}
        with httpx.Client(timeout=10.0) as client:
            r = client.post(endpoint, headers=self.headers, json=payload)
            r.raise_for_status()
            return r.json()

