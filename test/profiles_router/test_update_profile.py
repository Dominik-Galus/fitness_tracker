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
UNPROCESSABLE_STATUS: int = 422


@pytest.mark.parametrize(("user_id", "updated_profile"), [
    (1,
        {
            "age": 15, "weight": 90, "height": 181,
        },
    ),
    (2,
        {
            "age": 18, "weight": 80, "height": 199,
        },
    ),
    (3,
        {
            "age": 36, "weight": 81.7, "height": 174,
        },
    ),
])
def test_update_profile(user_id: int, updated_profile: dict[str, float], test_database: Session) -> None:
    fill_database(test_database)

    response = client.put(f"/profile/update/{user_id}", json=updated_profile)
    assert response.status_code == OK_STATUS

    profile = client.get(f"/profile/{user_id}").json()
    assert profile["age"] == updated_profile["age"]
    assert profile["weight"] == updated_profile["weight"]
    assert profile["height"] == updated_profile["height"]


@pytest.mark.parametrize(("user_id", "updated_profile"), [
    (1,
        {
            "age": -10, "weight": 90, "height": 181,
        },
    ),
    (2,
        {
            "age": 18, "weight": -123, "height": 199,
        },
    ),
    (3,
        {
            "age": 36, "weight": 81.7, "height": 0,
        },
    ),
])
def test_update_profile_failed(user_id: int, updated_profile: dict[str, float], test_database: Session) -> None:
    fill_database(test_database)

    response = client.put(f"/profile/update/{user_id}", json=updated_profile)
    assert response.status_code == UNPROCESSABLE_STATUS
