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

TESTING_DATABASE_URL: str | None = os.getenv("TESTING_DATABASE_URL")
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
NOT_FOUND_STATUS: int = 404


@pytest.mark.parametrize(("training_id", "updated_training"), [
    (1,
        [
            {
                "set_id": 1,
                "exercise_name": "Australian pull-ups",
                "repetitions": 10,
                "weight": 65,
            },
            {
                "exercise_name": "Australian pull-ups",
                "repetitions": 12,
                "weight": 55,
            },
        ],
    ),
    (2,
        [
            {
                "exercise_name": "Decline Pushups",
                "repetitions": 12,
                "weight": 55,
            },
            {
                "exercise_name": "Decline Pushups",
                "repetitions": 11,
                "weight": 0,
            },

        ],
    ),

])
def test_update_training(
    training_id: int,
    updated_training: list[dict[str, str | int]],
    test_database: Session,
) -> None:
    fill_database(test_database)
    response = client.put(f"/trainings/update/{training_id}", json=updated_training)
    assert response.status_code == OK_STATUS


@pytest.mark.parametrize(("training_id", "updated_training"), [
    (10,
        [
            {
                "set_id": 1,
                "exercise_name": "Australian pull-ups",
                "repetitions": 10,
                "weight": 65,
            },
            {
                "exercise_name": "Australian pull-ups",
                "repetitions": 12,
                "weight": 55,
            },
        ],
    ),
    (2,
        [
            {
                "exercise_name": "123321",
                "repetitions": 12,
                "weight": 55,
            },
            {
                "exercise_name": "wrong exercise",
                "repetitions": 11,
                "weight": 0,
            },

        ],
    ),

])
def test_update_training_failed(
    training_id: int,
    updated_training: list[dict[str, str | int]],
    test_database: Session,
) -> None:
    fill_database(test_database)
    response = client.put(f"/trainings/update/{training_id}", json=updated_training)
    assert response.status_code == NOT_FOUND_STATUS
