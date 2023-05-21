import datetime
from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    text: str
    role: Literal["human", "ai"] = "human"


class ChatMessageTime(ChatMessage):
    time: datetime.datetime


class ChatPrediction(BaseModel):
    prediction: str
    context: str | None
    instruction: str | None
    instance_id: int
    generation_info: dict