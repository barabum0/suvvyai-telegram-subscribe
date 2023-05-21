import typing
from typing import List

import httpx
from httpx import Response
from httpx._types import URLTypes

from suvvy.models.Chat import ChatMessage, ChatPrediction
from suvvy.models.Error import AuthenticationError, NotThatModel, ModelLimitExceeded
from suvvy.models.Instruct import InstructPrediction
from suvvy.models.Integration import TelegramIntegrationSettings


class SuvvyBotAPI:
    def __init__(self, bot_token: str, api_url: typing.Optional[str] = None, timeout_seconds: int = 3600):
        self.bot_token = bot_token
        self._default_header = {
            "Authorization": f"Bearer {self.bot_token}"
        }
        self.url = api_url or "https://api.suvvy.ai"
        self._timeout_seconds = timeout_seconds

        with httpx.Client() as c:
            r = c.get(self.url+"/api/check", headers=self._default_header, timeout=self._timeout_seconds)
            if r.text != "\"OK!\"":
                raise AuthenticationError("Invalid token or URL")

    async def _get_request(self, url: URLTypes) -> Response:
        async with httpx.AsyncClient() as client:
            r = await client.get(url=self.url+url, timeout=self._timeout_seconds, headers=self._default_header)

        return r

    async def _post_request(self, url: URLTypes, content: str | dict | list) -> Response:
        async with httpx.AsyncClient() as client:
            if isinstance(content, dict | list):
                r = await client.post(url=self.url+url, timeout=self._timeout_seconds, headers=self._default_header, json=content)
            else:
                r = await client.post(url=self.url+url, timeout=self._timeout_seconds, headers=self._default_header, content=content)

        return r

    async def _put_request(self, url: URLTypes, content: str | dict | list) -> Response:
        async with httpx.AsyncClient() as client:
            if isinstance(content, dict | list):
                r = await client.put(url=self.url+url, timeout=self._timeout_seconds, headers=self._default_header, json=content)
            else:
                r = await client.put(url=self.url+url, timeout=self._timeout_seconds, headers=self._default_header, content=content)

        return r

    async def _delete_request(self, url: URLTypes) -> Response:
        async with httpx.AsyncClient() as client:
            r = await client.delete(url=self.url+url, timeout=self._timeout_seconds, headers=self._default_header)

        return r

    async def chat_predict(self, history: List[ChatMessage], placeholders: dict = {}) -> ChatPrediction:
        if placeholders:
            r = await self._post_request("/api/v1/predict/chat/placeholder", content={
                "prompt": [m.dict() for m in history],
                "placeholders": placeholders
            })
        else:
            r = await self._post_request("/api/v1/predict/chat", content=[
                m.dict() for m in history
            ])

        d = r.json()
        match r.status_code:
            case 200:
                return ChatPrediction(**d)
            case 400:
                raise NotThatModel(d["error"])
            case 401:
                raise AuthenticationError()
            case 413:
                raise ModelLimitExceeded()

    async def instruct_predict(self, prompt: str, placeholders: dict = {}) -> InstructPrediction:
        if placeholders:
            r = await self._post_request("/api/v1/predict/instruct/placeholder", content={
                "prompt": prompt,
                "placeholders": placeholders
            })
        else:
            r = await self._post_request("/api/v1/predict/instruct", content=f"\"{prompt}\"")

        d = r.json()
        match r.status_code:
            case 200:
                return InstructPrediction(**d)
            case 400:
                ret = await self.chat_predict(history=[
                    ChatMessage(text=prompt)
                ], placeholders=placeholders)
                return InstructPrediction(**ret.dict())
            case 401:
                raise AuthenticationError()
            case 413:
                raise ModelLimitExceeded()
            case _:
                print(r.content)
                print(r.status_code)

    async def get_telegram_settings(self) -> TelegramIntegrationSettings:
        r = await self._get_request("/api/integration/telegram")

        d = r.json()
        match r.status_code:
            case 200:
                return TelegramIntegrationSettings(**d)
            case 401:
                raise AuthenticationError(d["error"])
