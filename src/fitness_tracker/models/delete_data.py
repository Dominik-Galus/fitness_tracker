from pydantic import BaseModel


class DeleteData(BaseModel):
    access_token: str
    password: str
