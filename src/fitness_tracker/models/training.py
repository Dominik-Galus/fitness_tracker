import datetime

from pydantic import BaseModel


class Training(BaseModel):
    training_name: str
    date: datetime.date
