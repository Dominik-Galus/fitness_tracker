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


@pytest.mark.parametrize(("user_id", "sort_by", "order", "expected_trainings"), [
    (
        2, "name", "asc", [
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
    (
        2, "name", "desc", [
            {
                "training_id": 3,
                "training_name": "test3",
                "date": "2025-02-21",
            },
            {
                "training_id": 2,
                "training_name": "test2",
                "date": "2025-02-23",
            },
        ],
    ),
    (
        2, "date", "asc", [
            {
                "training_id": 3,
                "training_name": "test3",
                "date": "2025-02-21",
            },
            {
                "training_id": 2,
                "training_name": "test2",
                "date": "2025-02-23",
            },
        ],
    ),
    (
        2, "date", "desc", [
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
])
def test_get_sorted_trainings(
    user_id: int,
    sort_by: str,
    order: str,
    expected_trainings: list[dict[str, str]],
    test_database: Session,
) -> None:
    fill_database(test_database)
    response = client.get(f"/trainings/fetch/sorted/{user_id}", params={"sort_by": sort_by, "order": order})
    assert response.status_code == OK_STATUS
    trainings = response.json()
    assert trainings == expected_trainings
