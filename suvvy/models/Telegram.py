from pydantic import BaseModel


class TelegramChannel(BaseModel):
    name: str
    id: int
    link: str