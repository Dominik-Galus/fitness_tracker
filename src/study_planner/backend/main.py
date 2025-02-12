from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from study_planner.backend import models
from study_planner.backend.database import SessionLocal, engine
from study_planner.backend.routers.authorization import authorization_router

planner_app = FastAPI()
planner_app.include_router(authorization_router)

models.Base.metadata.create_all(bind=engine)


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


database_dependency = Annotated[Session, Depends(get_database)]
