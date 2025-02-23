# ruff: noqa: S101
import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fitness_tracker.database import Base
from fitness_tracker.main import fitness_app, get_database
from test.database_filler import fill_database

TESTING_DATABASE_URL: str | None = os.getenv("DATABASE_URL")
if not TESTING_DATABASE_URL:
    msg = "Missing url for testing database"
    raise ValueError(msg)

engine = create_engine(TESTING_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_database() -> Generator:
    try:
        database = TestingSessionLocal()
        yield database
    finally:
        database.close()


@pytest.fixture
def test_database() -> Generator:
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)


fitness_app.dependency_overrides[get_database] = override_get_database
client = TestClient(fitness_app)

OK_STATUS: int = 200
BAD_REQUEST_STATUS: int = 400


@pytest.mark.parametrize("training_id", [
    1, 2, 3,
])
def test_delete_training(training_id: int, test_database: Session) -> None:
    fill_database(test_database)
    response = client.delete(f"/trainings/delete/{training_id}")
    assert response.status_code == OK_STATUS
