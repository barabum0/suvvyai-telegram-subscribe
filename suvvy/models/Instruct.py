from pydantic import BaseModel


class InstructPrediction(BaseModel):
    prediction: str
    context: str | None
    instruction: str | None
    instance_id: int
    generation_info: dict