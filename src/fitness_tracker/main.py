import os
from collections.abc import Generator
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from fitness_tracker import models
from fitness_tracker.database import SessionLocal, engine
from fitness_tracker.routers.authorization import authorization_router

load_dotenv()

fitness_app = FastAPI()
fitness_app.include_router(authorization_router)

models.Base.metadata.create_all(bind=engine)

frontend_url: str | None = os.getenv("FRONTEND_URL")
if frontend_url is None:
    msg = "Missing frontend url"
    raise ValueError(msg)

fitness_app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


database_dependency = Annotated[Session, Depends(get_database)]
