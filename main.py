import asyncio
import datetime
import logging
from os import getenv
from typing import Any

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv

from channels import get_telegram_channels, ChannelMiddleware, check_subscribe
from database import Database, create_db_connection
from suvvy.models.Chat import ChatMessage, ChatMessageTime
from suvvy.models.Integration import TelegramIntegrationSettings
from suvvy.suvvy_ai import SuvvyBotAPI
from suvvy_middleware import SuvvyMiddleware

bot = Bot(token=getenv('TELEGRAM_BOT_TOKEN'), parse_mode='HTML')
dp = Dispatcher()
load_dotenv()


class Questionary(StatesGroup):
    q_1 = State()
    q_2 = State()


async def get_state_param(state: FSMContext, key: str, default: Any = None) -> Any:
    data = await state.get_data()
    return data.get(key, default)


async def set_state_param(state: FSMContext, key: str, value: Any):
    data = await state.get_data()
    data[key] = value
    await state.set_data(data)


async def add_history_message(state: FSMContext, text: str, role: str):
    suvvy_message = ChatMessageTime(text=text, role=role, time=datetime.datetime.now())
    history = await get_state_param(state, 'history', [])
    history.append(suvvy_message)
    await set_state_param(state, "history", history)


async def get_history(state: FSMContext, key: str = "history", time: bool = False) -> list[ChatMessage | ChatMessageTime]:
    history = await get_state_param(state, key, [])
    if time:
        return history
    else:
        return [ChatMessage(**h.dict()) for h in history]


@dp.message(F.text.startswith("/start"))
async def on_start(message: Message, state: FSMContext):
    db = Database(create_db_connection())
    if await db.check_questions(message.from_user.id):
        await state.clear()
        text = f"""
Отправьте мне любое сообщение для начала работы!
            """
        await message.reply(text)
    else:
        text = f"""
    Привет, <b>{message.from_user.full_name}</b>!
    
Для использования бота вам необходимо заполнить небольшую анкету!
    """
        await message.reply(text)

        text = f"""
    Отправьте мне <b>ваше имя</b>
        """
        await message.answer(text)
        await state.set_state(Questionary.q_1)


@dp.message(Questionary.q_1)
async def on_q1(message: Message, state: FSMContext):
    # text = f"""Отличное имя, <b>{message.text}</b>!"""
    # await message.reply(text)
    text = f"""Теперь отправьте мне <b>вашу должность</b>"""
    await message.answer(text)
    await set_state_param(state, "q_1", message.text)
    await state.set_state(Questionary.q_2)


@dp.message(Questionary.q_2)
async def on_q2(message: Message, state: FSMContext):
    db = Database(create_db_connection())
    # text = f"""Интересная у вас работа!"""
    # await message.reply(text)
    await set_state_param(state, "q_2", message.text)
    await db.add_questions_to_db({
        "uid": message.from_user.id,
        "name": await get_state_param(state, "q_1", ""),
        "job": message.text
    })
    return await on_start(message, state)


@dp.message()
async def on_message(message: Message, state: FSMContext, suvvy: SuvvyBotAPI, telegram_settings: TelegramIntegrationSettings, bot: Bot):
    messages_be = await get_history(state, time=True)
    db = Database(create_db_connection())
    await add_history_message(state, message.text, 'human')
    if telegram_settings.merge_messages:
        time = datetime.datetime.now().replace(microsecond=0)
        await set_state_param(state, "merge_time", time)
        await asyncio.sleep(telegram_settings.merge_wait_time_seconds)
        new_time = (await state.get_data())['merge_time'].replace(microsecond=0)
        if new_time != time:
            return

    history = await get_history(state)
    print(history)

    await bot.send_chat_action(message.chat.id, "typing")

    match telegram_settings.history_type:
        case "disabled":
            result = await suvvy.chat_predict(history)
            await set_state_param(state, "history", [])
        case "enabled":
            result = await suvvy.chat_predict(history)
            await add_history_message(state, result.prediction, 'ai')
        case "last_time":
            h = await get_history(state, time=True)
            ms = [
                ChatMessage(**mes.dict()) for mes in h if
                datetime.datetime.now() - mes.time < datetime.timedelta(minutes=telegram_settings.history_time_minutes)
            ]
            result = await suvvy.chat_predict(ms)
            await add_history_message(state, result.prediction, 'ai')
        case "auto_reset_time":
            if len(messages_be) != 0:
                if datetime.datetime.now() - messages_be[-1].time > datetime.timedelta(
                        minutes=telegram_settings.history_time_minutes):
                    if telegram_settings.system_messages:
                        await message.answer("💥 История <b>была сброшена</b> в связи с простоем!", parse_mode="HTML")
                    await set_state_param(state, "history", [])
            extra = await db.get_questions(message.from_user.id)
            extra["username"] = message.from_user.username or "N/A"
            extra["url"] = message.from_user.url or "N/A"
            result = await suvvy.chat_predict(history[len(messages_be)-1:], custom_log_info=extra)
        case _:
            result = await suvvy.chat_predict(history)
            await set_state_param(state, "history", [])

    await message.answer(result.prediction, parse_mode="Markdown")


@dp.callback_query(F.data == "check_subscribe")
async def check_sub(query: CallbackQuery, bot: Bot):
    not_member = await check_subscribe(get_telegram_channels(), bot, query.from_user.id)
    if not not_member:
        await query.message.delete()
        await query.answer("Приятного пользования!")
        return await on_start(query.message)
    else:
        await query.answer("Вы не подписались на все каналы!", show_alert=True)


async def main() -> None:
    dp.message.middleware(ChannelMiddleware(get_telegram_channels()))
    dp.message.middleware(SuvvyMiddleware(SuvvyBotAPI(getenv('SUVVY_TOKEN'))))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())