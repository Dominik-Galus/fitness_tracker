from pydantic import BaseModel


class ExerciseSet(BaseModel):
    exercise_name: str
    repetitions: int
    weight: float
