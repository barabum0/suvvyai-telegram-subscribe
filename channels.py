from typing import Callable, Any, Awaitable

import yaml
from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from suvvy.models.Telegram import TelegramChannel


def get_telegram_channels():
    ch = yaml.safe_load(open("telegram.yaml"))
    ch: dict = ch['channels']
    ch: list = list(ch.values())

    return [TelegramChannel(**h) for h in ch]


async def check_subscribe(channels, bot, uid):
    try:
        not_a_member = []
        for channel in channels:
            member = await bot.get_chat_member(channel.id, uid)
            if member.status == "left":
                not_a_member.append(channel)

        return not_a_member
    except TelegramBadRequest as e:
        if e.message == "Bad Request: chat not found":
            return []
        else:
            raise


class ChannelMiddleware(BaseMiddleware):
    def __init__(self, channels: list[TelegramChannel]) -> None:
        self.channels = channels

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        not_a_member = await check_subscribe(self.channels, data['bot'], event.from_user.id)

        if not_a_member:
            text = """
        Для <b>продолжения работы с ботом</b> вам необходимо <b>подписаться</b> на эти каналы:
        """
            keyboard = InlineKeyboardMarkup(
                resize_keyoard=True,
                inline_keyboard=[
                                    [InlineKeyboardButton(text=channel.name, url=channel.link)] for channel in
                                    not_a_member
                                ] + [[InlineKeyboardButton(text="Я подписался!", callback_data="check_subscribe")]]
            )
            await event.answer(text, reply_markup=keyboard)
            return

        return await handler(event, data)