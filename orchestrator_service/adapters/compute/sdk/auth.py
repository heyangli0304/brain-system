"""
算力适配 - Token管理
整合自同事的 compute_adapter_service/sdk/auth.py
支持 Mock 模式（本地测试）和真实算力控制器调用
"""
import time
from typing import Dict, Any, Optional

MOCK_TOKEN = "compute-brain-token-20260422"
MOCK_REFRESH_TOKEN = "compute-brain-refresh-token-20260422"

USE_MOCK = True


class AuthClient:

    def __init__(self, base_url: str = "http://算力控制器IP:8001"):
        self.base_url = base_url
        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expire_time: float = 0

    def login(self, username: str, password: str) -> Dict[str, Any]:
        if USE_MOCK:
            if username == "admin" and password == "123456":
                self._token = MOCK_TOKEN
                self._refresh_token = MOCK_REFRESH_TOKEN
                self._token_expire_time = time.time() + 3600
                return {
                    "respCode": 0, "respError": "", "respMessage": "success",
                    "respBody": {
                        "token": MOCK_TOKEN,
                        "refresh_token": MOCK_REFRESH_TOKEN,
                        "expires_in": 3600,
                        "core-sctoken": MOCK_TOKEN,
                    },
                    "custCode": 0,
                }
            return {
                "respCode": 1, "respError": "auth failed",
                "respMessage": "invalid credentials", "respBody": {}, "custCode": 0,
            }

        import requests
        url = f"{self.base_url}/auth/token"
        payload = {"username": username, "password": password}
        response = requests.post(url, json=payload)
        result = response.json()
        if result.get("respCode") == 0:
            body = result.get("respBody", {})
            self._token = body.get("token", "")
            self._refresh_token = body.get("refresh_token", "")
            expires_in = body.get("expires_in", 3600)
            self._token_expire_time = time.time() + expires_in
        return result

    def refresh(self) -> Dict[str, Any]:
        if USE_MOCK:
            self._token_expire_time = time.time() + 3600
            return {"respCode": 0, "respError": "", "respMessage": "success", "respBody": {}, "custCode": 0}

        import requests
        url = f"{self.base_url}/auth/token/refresh"
        payload = {"refresh_token": self._refresh_token}
        response = requests.post(url, json=payload)
        result = response.json()
        if result.get("respCode") == 0:
            body = result.get("respBody", {})
            self._token = body.get("token", self._token)
            self._refresh_token = body.get("refresh_token", self._refresh_token)
            expires_in = body.get("expires_in", 3600)
            self._token_expire_time = time.time() + expires_in
        return result

    @property
    def token(self) -> str:
        if self._token is None:
            raise RuntimeError("还没登录！请先调用 login(username, password)")
        if time.time() >= self._token_expire_time and self._refresh_token:
            self.refresh()
        return self._token

    @property
    def auth_header(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}
