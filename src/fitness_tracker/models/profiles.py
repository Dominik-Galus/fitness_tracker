from typing import Annotated

from pydantic import AfterValidator, BaseModel

from fitness_tracker.models.validators import is_positive_number


class Profiles(BaseModel):
    user_id: int | None = None
    age: Annotated[int, AfterValidator(is_positive_number)]
    weight: Annotated[float, AfterValidator(is_positive_number)]
    height: Annotated[int, AfterValidator(is_positive_number)]
