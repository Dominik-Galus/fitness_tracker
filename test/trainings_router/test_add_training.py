# ruff: noqa: S101
import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fitness_tracker.database import Base
from fitness_tracker.main import fitness_app, get_database
from test.database_filler import fill_users

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

CREATED_STATUS: int = 201
UNPROCESSABLE_STATUS: int = 422
BAD_REQUEST: int = 400


@pytest.mark.parametrize(("user_id", "training_data", "sets"), [
    (1,
        {
            "training_name": "test1",
            "date": "2025-02-23",
        },
        [
            {
                "exercise_name": "Australian pull-ups",
                "repetitions": 12,
                "weight": 70,
            },
        ],
    ),
    (2,
        {
            "training_name": "test2",
            "date": "2025-02-23",
        },
        [
            {
                "exercise_name": "Decline Pushups",
                "repetitions": 12,
                "weight": 0,
            },
            {
                "exercise_name": "Bench Press",
                "repetitions": 12,
                "weight": 100,
            },
            {
                "exercise_name": "Bench Press",
                "repetitions": 12,
                "weight": 100,
            },

        ],
    ),
])
def test_add_training(
    user_id: int,
    training_data: dict[str, str],
    sets: list[dict[str, int]],
    test_database: Session,
) -> None:
    fill_users(test_database)
    response = client.post("/trainings/", params={"user_id": user_id}, json={"training": training_data, "sets": sets})
    assert response.status_code == CREATED_STATUS


@pytest.mark.parametrize(("user_id", "training_data", "sets"), [
    (1,
        {
            "training_name": "test1",
            "date": "2025-02-23",
        },
        [
            {
                "exercise_name": "Australian pull-ups",
                "repetitions": 0,
                "weight": 70,
            },
        ],
    ),
    (2,
        {
            "training_name": "test2",
            "date": "2025-02-23",
        },
        [
            {
                "exercise_name": "Decline Pushups",
                "repetitions": 12,
                "weight": -12,
            },
            {
                "exercise_name": "Bench Press",
                "repetitions": -13,
                "weight": -123,
            },
            {
                "exercise_name": "Bench Press",
                "repetitions": 12,
                "weight": 100,
            },

        ],
    ),
    (3,
        {
            "training_name": "test1",
            "date": "2025-02-23",
        },
        [
            {
                "exercise_name": "not existing exercise",
                "repetitions": 12,
                "weight": 70,
            },
        ],
    ),

])
def test_add_training_failed(
    user_id: int,
    training_data: dict[str, str],
    sets: list[dict[str, int]],
    test_database: Session,
) -> None:
    fill_users(test_database)
    response = client.post("/trainings/", params={"user_id": user_id}, json={"training": training_data, "sets": sets})
    assert response.status_code in {UNPROCESSABLE_STATUS, BAD_REQUEST}
