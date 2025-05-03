from datetime import datetime
from pydantic import BaseModel

class AlertMsg(BaseModel):
    symbol: str
    price: float
    timestamp: datetime

class AckMsg(BaseModel):
    detail: str