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


@pytest.mark.parametrize(("characters", "user_id", "expected_trainings"), [
    ("tes", "1",
        [
            {
                "training_id": 1,
                "training_name": "test1",
                "date": "2025-02-23",
            },

        ],
    ),
    ("t", "2",
        [
            {
                "training_id": 2,
                "training_name": "test2",
                "date": "2025-02-23",
            },
            {
                "training_id": 3,
                "training_name": "test3",
                "date": "2025-02-21",
            },
        ],
    ),
    ("test2", "2",
        [
            {
                "training_id": 2,
                "training_name": "test2",
                "date": "2025-02-23",
            },
        ],
    ),
])
def test_get_trainings_by_chars(
    characters: str,
    user_id: int,
    expected_trainings: list[dict[str, str | int]],
    test_database: Session,
) -> None:
    fill_database(test_database)
    response = client.get("/trainings/fetch/search", params={"characters": characters, "user_id": user_id})
    assert response.status_code == OK_STATUS
    trainings = response.json()
    assert trainings == expected_trainings
