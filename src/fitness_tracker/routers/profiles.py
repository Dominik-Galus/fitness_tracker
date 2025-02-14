from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from fitness_tracker.database import SessionLocal
from fitness_tracker.models.profiles import Profiles
from fitness_tracker.models.user_profile import UserProfile
from fitness_tracker.routers.authorization import SUCCESS_USER_CREATE

profiles_router = APIRouter(prefix="/profile", tags=["user_profile"])
USER_ID_KEY: str = "user_profile_user_id_key"


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


database_dependency = Annotated[Session, Depends(get_database)]

CREATION_SUCCESS: dict[str, bool] = {"status": True}


@profiles_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_profile(
    database: database_dependency,
    user_profile: Profiles,
) -> dict[str, bool]:
    try:
        profile_model = UserProfile(
            user_id=user_profile.user_id,
            height=user_profile.height,
            weight=user_profile.weight,
            age=user_profile.age,
        )

        database.add(profile_model)
        database.commit()

    except IntegrityError as e:
        if USER_ID_KEY in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile for this user already exists.",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        ) from e

    else:
        return SUCCESS_USER_CREATE


@profiles_router.get("/{user_id}")
async def get_profile(user_id: int, database: database_dependency) -> Profiles | None:
    profile = database.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile for this user does not exists.",
        )
    return Profiles(
        user_id=user_id,
        age=profile.age,
        height=profile.height,
        weight=float(profile.weight),
    )
