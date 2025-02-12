import os
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from study_planner.backend.configs.access_token import PAYLOAD_ID, PAYLOAD_SUB, TIME_EXPIRES
from study_planner.backend.database import SessionLocal
from study_planner.backend.models.auth_token import AuthToken
from study_planner.backend.models.create_user_request import CreateUserRequest
from study_planner.backend.models.users import Users

load_dotenv()

authorization_router = APIRouter(prefix="/auth", tags=["authorization"])

SECRET_KEY: str | None = os.getenv("SECRET_KEY")
ALGORITHM: str | None = os.getenv("ALGORITHM")

SUCCESS_USER_CREATE: dict[str, bool] = {"status": True}
USERNAME_KEY: str = "users_username_key"
EMAIL_KEY: str = "users_email_key"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


database_dependency = Annotated[Session, Depends(get_database)]


@authorization_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(database: database_dependency, create_user_request: CreateUserRequest) -> dict[str, bool]:
    try:
        create_user_model = Users(
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
    else:
        return SUCCESS_USER_CREATE


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
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return AuthToken(access_token=token, token_type="bearer")  # noqa: S106


def authenticate_user(username: str, password: str, database: database_dependency) -> Users | None:
    user = database.query(Users).filter(Users.username == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.password):
        return None
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta) -> str:
    if not SECRET_KEY or not ALGORITHM:
        msg = "There is no secret key or algorithm"
        raise ValueError(msg)
    encode = {PAYLOAD_SUB: username, PAYLOAD_ID: user_id}
    expires = datetime.now(UTC) + expires_delta
    encode.update({TIME_EXPIRES: expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
