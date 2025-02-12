import os
from collections.abc import Generator
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from study_planner.backend.database import SessionLocal
from study_planner.backend.models.create_user_request import CreateUserRequest
from study_planner.backend.models.users import Users

load_dotenv()

authorization_router = APIRouter(prefix="/auth", tags=["authorization"])

SECRET_KEY: str | None = os.getenv("SECRET_KEY")
ALGORITHM: str = "HS256"
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
        return {"status": True}
