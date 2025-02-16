import datetime

from pydantic import BaseModel


class Training(BaseModel):
    training_id: int
    training_name: str
    date: datetime.date
