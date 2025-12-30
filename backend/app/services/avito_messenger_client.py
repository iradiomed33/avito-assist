import httpx


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
