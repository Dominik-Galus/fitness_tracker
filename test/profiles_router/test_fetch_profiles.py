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


@pytest.mark.parametrize(("user_id", "expected_profile"), [
    (1,
        {
            "age": 15, "weight": 75, "height": 180,
        },
    ),
    (2,
        {
            "age": 18, "weight": 120, "height": 200,
        },
    ),
    (3,
        {
            "age": 35, "weight": 83, "height": 175,
        },
    ),
])
def test_fetch_profiles(user_id: int, expected_profile: dict[str, int], test_database: Session) -> None:
    fill_database(test_database)
    response = client.get(f"/profile/{user_id}")
    assert response.status_code == OK_STATUS

    profile = response.json()
    assert profile["age"] == expected_profile["age"]
    assert profile["weight"] == expected_profile["weight"]
    assert profile["height"] == expected_profile["height"]
