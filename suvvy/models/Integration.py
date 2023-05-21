from datetime import timedelta
from typing import Literal

from pydantic import BaseModel


class TelegramIntegrationSettings(BaseModel):
    bot_token: str = ""
    bot_enabled: bool = False
    bot_banned: bool = False

    instance_token: str = ""
    instance_type: Literal["chat", "instruct"] = "chat"

    history_type: Literal["last_time", "disabled", "enabled", "auto_reset_time"] = "disabled"
    history_time_minutes: int = 60

    regenerate_button: bool = False

    max_per_day: int = 10
    max_symbols: int = 300

    system_messages: bool = True

    merge_messages: bool = False
    merge_wait_time_seconds: int = 15