from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from fitness_tracker.database import SessionLocal

trainings_router = APIRouter("/trainings", tags=["trainings"])


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


database_dependency = Annotated[Session, Depends(get_database)]


@trainings_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_training(user_id: int) -> None:
    pass
