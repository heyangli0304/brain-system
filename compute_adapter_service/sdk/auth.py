"""
算力南向适配服务 - Token管理
文件位置：compute_adapter_service/sdk/auth.py
处理 Token 获取与刷新
"""

import requests
import time


class AuthClient:

    def __init__(self, base_url):
        self.base_url = base_url
        self._token = None
        self._refresh_token = None
        self._token_expire_time = 0

    def login(self, username, password):
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

    def refresh(self):
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
    def token(self):
        if self._token is None:
            raise RuntimeError("还没登录！请先调用 login(username, password)")
        if time.time() >= self._token_expire_time and self._refresh_token:
            self.refresh()
        return self._token

    @property
    def auth_header(self):
        return {"Authorization": f"Bearer {self.token}"}
