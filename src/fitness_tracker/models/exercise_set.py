from typing import Annotated

from pydantic import AfterValidator, BaseModel

from fitness_tracker.models.validators import is_non_negative, is_positive_number


class ExerciseSet(BaseModel):
    set_id: int | None = None
    exercise_name: str
    repetitions: Annotated[int, AfterValidator(is_positive_number)]
    weight: Annotated[float, AfterValidator(is_non_negative)]
