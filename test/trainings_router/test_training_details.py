# ruff: noqa: S101
import os
from collections.abc import Generator
from datetime import date

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


@pytest.mark.parametrize(("training_id", "expected_training_details"), [
    (1,
        {
            "name": "test1",
            "date": "2025-02-23",
            "sets": [
                {
                    "set_id": 1,
                    "exercise_name": "Australian pull-ups",
                    "repetitions": 12,
                    "weight": 70,
                },
            ],
        },
    ),
])
def test_training_details(
    training_id: int,
    expected_training_details: dict[str, list[dict[str, str | int] | int | date]],
    test_database: Session,
) -> None:
    fill_database(test_database)
    response = client.get(f"/trainings/details/{training_id}")
    assert response.status_code == OK_STATUS
    training_details = response.json()
    assert training_details == expected_training_details
