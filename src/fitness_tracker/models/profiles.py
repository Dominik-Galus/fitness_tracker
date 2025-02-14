from pydantic import BaseModel


class Profiles(BaseModel):
    user_id: int | None = None
    age: int
    weight: float
    height: int
