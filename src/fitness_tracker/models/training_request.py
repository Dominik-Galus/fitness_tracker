from datetime import date

from pydantic import BaseModel


class TrainingRequest(BaseModel):
    training_name: str
    date: date
