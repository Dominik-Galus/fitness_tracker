# ruff: noqa: S101
import os
from collections.abc import Generator

import pytest
from _pytest.fixtures import FixtureFunction
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fitness_tracker.database import Base
from fitness_tracker.main import fitness_app, get_database

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
    yield
    Base.metadata.drop_all(bind=engine)


fitness_app.dependency_overrides[get_database] = override_get_database
client = TestClient(fitness_app)

CREATED_STATUS: int = 201
FAILED_STATUS: int = 400


@pytest.mark.parametrize(("user"), [
    {"username": "test1", "email": "email1@email.com", "password": "test2"},
    {"username": "test3", "email": "email2@email.com", "password": "test4"},
    {"username": "test5", "email": "email3@email.com", "password": "test6"},
])
def test_create_user(user: dict[str, str], test_database: FixtureFunction) -> None:  # noqa: ARG001
    response = client.post("/auth/", json=user)
    assert response.status_code == CREATED_STATUS


@pytest.mark.parametrize(("first_user", "second_user"), [
    (
        {"username": "test1", "email": "email1@email.com", "password": "test"},
        {"username": "test1", "email": "email2@email.com", "password": "test"},
    ),
    (
        {"username": "test1", "email": "email1@email.com", "password": "test"},
        {"username": "test2", "email": "email1@email.com", "password": "test"},
    ),

])
def test_create_user_failed(
    first_user: dict[str, str],
    second_user: dict[str, str],
    test_database: FixtureFunction,  # noqa: ARG001
) -> None:
    response_first_user = client.post("/auth/", json=first_user)
    assert response_first_user.status_code == CREATED_STATUS

    response_second_user = client.post("/auth/", json=second_user)
    assert response_second_user.status_code == FAILED_STATUS
