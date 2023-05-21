import datetime

from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    bot_id: int
    messages: dict = {}
    daily: int = 0
    last_message_date: datetime.datetime
    merge_message_time: datetime.datetime
