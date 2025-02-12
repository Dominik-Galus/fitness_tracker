from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from fitness_tracker.backend import models
from fitness_tracker.backend.database import SessionLocal, engine
from fitness_tracker.backend.routers.authorization import authorization_router

fitness_app = FastAPI()
fitness_app.include_router(authorization_router)

models.Base.metadata.create_all(bind=engine)


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


database_dependency = Annotated[Session, Depends(get_database)]
