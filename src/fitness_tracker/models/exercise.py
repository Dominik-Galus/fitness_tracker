from pydantic import BaseModel


class Exercise(BaseModel):
    exercise_name: str
    muscle_group: str
