from pydantic import BaseModel


class ExerciseSet(BaseModel):
    set_id: int | None = None
    exercise_name: str
    repetitions: int
    weight: float
