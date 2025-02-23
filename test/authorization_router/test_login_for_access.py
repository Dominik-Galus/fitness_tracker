# ruff: noqa: S101
import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fitness_tracker.database import Base
from fitness_tracker.main import fitness_app, get_database

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
NOT_AUTHORIZED_STATUS: int = 401


@pytest.mark.parametrize(("user"), [
    {"username": "test1", "email": "email1@email.com", "password": "test2"},
    {"username": "test3", "email": "email2@email.com", "password": "test4"},
    {"username": "test5", "email": "email3@email.com", "password": "test6"},
])
def test_login_for_access(user: dict[str, str], test_database: Session) -> None:  # noqa: ARG001
    client.post("/auth/", json=user)
    response = client.post("/auth/token", data=user)
    assert response.status_code == OK_STATUS
    assert response.json() is not None


@pytest.mark.parametrize(("user", "wrong_password"), [
    ({"username": "test1", "email": "email1@email.com", "password": "test2"}, "wrong"),
    ({"username": "test3", "email": "email2@email.com", "password": "test4"}, "wrong"),
    ({"username": "test5", "email": "email3@email.com", "password": "test6"}, "wrong"),
])
def test_login_for_access_failed(user: dict[str, str], wrong_password: str, test_database: Session) -> None:  # noqa: ARG001
    client.post("/auth/", json=user)
    response = client.post("/auth/token", data={"username": user["username"], "password": wrong_password})
    assert response.status_code == NOT_AUTHORIZED_STATUS
