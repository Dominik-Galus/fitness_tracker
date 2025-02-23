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


@pytest.mark.parametrize(("characters", "expected_response"), [
    ("up", [
        {
            "exercise_name": "Australian pull-ups",
            "muscle_group": "Shoulders, Biceps, Lats",
        },
        {
            "exercise_name": "Chin-ups",
            "muscle_group": "Lats",
        },
        {
            "exercise_name": "Close-grip Press-ups",
            "muscle_group": "Lats, Chest",
        },
        {
            "exercise_name": "Crunches With Legs Up",
            "muscle_group": "Abs",
        },
        {
            "exercise_name": "Decline Pushups",
            "muscle_group": "Chest",
        },
    ]),
    ("bench", [
        {
            "exercise_name": "Barbell Bench Press - NB",
            "muscle_group": "Chest",
        },
        {
            "exercise_name": "Bench Dips On Floor HD",
            "muscle_group": "Biceps, Triceps",
        },
        {
            "exercise_name": "Bench Press",
            "muscle_group": "Chest",
        },
        {
            "exercise_name": "Bench Press Narrow Grip",
            "muscle_group": "Triceps",
        },
        {
            "exercise_name": "Benchpress Dumbbells",
            "muscle_group": "Chest",
        },
    ]),
    ("123;'[]", None,
    ),
])
def test_get_exercises_by_characters(
    characters: str,
    expected_response: list[dict[str, str]],
    test_database: Session,
) -> None:
    fill_database(test_database)
    response = client.get("/exercise/search", params={"characters": characters})
    assert response.status_code == 200  # noqa: PLR2004
    assert response.json() == expected_response
