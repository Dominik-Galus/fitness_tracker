import os
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from fitness_tracker.configs.access_token import PAYLOAD_ID, PAYLOAD_SUB, TIME_EXPIRES
from fitness_tracker.database import SessionLocal
from fitness_tracker.models.auth_token import AuthToken
from fitness_tracker.models.create_user_request import CreateUserRequest
from fitness_tracker.tables.users_table import UsersTable

load_dotenv()

authorization_router = APIRouter(prefix="/auth", tags=["authorization"])

SECRET_KEY: str | None = os.getenv("SECRET_KEY")
ALGORITHM: str | None = os.getenv("ALGORITHM")

USERNAME_KEY: str = "users_username_key"
EMAIL_KEY: str = "users_email_key"
REFRESH_TOKEN_EXPIRE_DAYS: int = 7
ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
security = HTTPBearer()


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


database_dependency = Annotated[Session, Depends(get_database)]


@authorization_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(database: database_dependency, create_user_request: CreateUserRequest) -> None:
    try:
        create_user_model = UsersTable(
            username=create_user_request.username,
            email=create_user_request.email,
            password=bcrypt_context.hash(create_user_request.password),
        )

        database.add(create_user_model)
        database.commit()
    except IntegrityError as e:
        if USERNAME_KEY in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists.",
            ) from e
        if EMAIL_KEY in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists.",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        ) from e


@authorization_router.post("/token")
async def login_for_access_token(
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    database: database_dependency,
) -> AuthToken:
    user = authenticate_user(login_form.username, login_form.password, database)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user",
        )
    access_token = create_access_token(user.username, user.id)

    refresh_token = create_refresh_token(user.username, user.id)

    return AuthToken(access_token=access_token, refresh_token=refresh_token, token_type="bearer")  # noqa: S106


def authenticate_user(username: str, password: str, database: database_dependency) -> UsersTable | None:
    user = database.query(UsersTable).filter(UsersTable.username == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.password):
        return None
    return user


def create_access_token(username: str, user_id: int) -> str:
    if not SECRET_KEY or not ALGORITHM:
        msg = "Missing SECRET_KEY or Algorithm"
        raise ValueError(msg)

    expires = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode = {PAYLOAD_SUB: username, PAYLOAD_ID: user_id, TIME_EXPIRES: expires.timestamp()}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(username: str, user_id: int) -> str:
    if not SECRET_KEY or not ALGORITHM:
        msg = "Missing SECRET_KEY or Algorithm"
        raise ValueError(msg)

    expires = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    encode = {PAYLOAD_SUB: username, PAYLOAD_ID: user_id, TIME_EXPIRES: expires.timestamp(), "type": "refresh"}

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@authorization_router.post("/refresh")
async def refresh_access_token(refresh_token: str, database: database_dependency) -> AuthToken:
    if SECRET_KEY is None or ALGORITHM is None:
        msg = "Missing SECRET_KEY or Algorithm"
        raise ValueError(msg)
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=ALGORITHM)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from e

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    username: str | None = payload.get(PAYLOAD_SUB)
    user_id: int | None = payload.get(PAYLOAD_ID)

    if username is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = database.query(UsersTable).filter(UsersTable.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(username, user_id)

    return AuthToken(
        access_token=access_token,
        token_type="bearer",  # noqa: S106
    )
