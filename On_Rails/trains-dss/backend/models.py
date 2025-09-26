from pydantic import BaseModel
from typing import List

class TrainInput(BaseModel):
    id: str
    current_position: str
    next_station: str
    priority: int
    platform: str

class TrainDelay(BaseModel):
    id: str
    predicted_delay: int
    optimal_delay: int
    new_platform: str
    delay_reason: str   # added for delay reason

class DelayRequest(BaseModel):
    trains: List[TrainInput]
    weather_condition: str

class DelayResponse(BaseModel):
    train_delays: List[TrainDelay]
