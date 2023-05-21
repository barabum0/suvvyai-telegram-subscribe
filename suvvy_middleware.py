from typing import Dict, Any, Callable, Awaitable

import httpx
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message

from suvvy.models.Error import AuthenticationError, TokenNotFound
from suvvy.suvvy_ai import SuvvyBotAPI


class SuvvyMiddleware(BaseMiddleware):
    def __init__(self, suvvy: SuvvyBotAPI) -> None:
        self.suvvy = suvvy

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        bot: Bot = data['bot']
        data["suvvy"] = self.suvvy
        data["telegram_settings"] = await self.suvvy.get_telegram_settings()
        return await handler(event, data)
