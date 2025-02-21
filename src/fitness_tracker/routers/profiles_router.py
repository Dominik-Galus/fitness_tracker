from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from fitness_tracker.database import SessionLocal
from fitness_tracker.models.profiles import Profiles
from fitness_tracker.tables.profile_table import ProfileTable

profiles_router = APIRouter(prefix="/profile", tags=["user_profile"])
USER_ID_KEY: str = "user_profile_user_id_key"


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


database_dependency = Annotated[Session, Depends(get_database)]


@profiles_router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_profile(user_id: int, database: database_dependency) -> Profiles | None:
    try:
        profile = database.query(ProfileTable).filter(ProfileTable.user_id == user_id).first()
        if not profile:
            profile = ProfileTable(
                user_id=user_id,
                age=None,
                weight=None,
                height=None,
            )
            database.add(profile)
            database.commit()
            database.refresh(profile)
    except IntegrityError as e:
        database.rollback()
        if USER_ID_KEY in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile for this user already exists.",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred. {e}",
        ) from e
    else:
        return Profiles(
            user_id=user_id,
            age=profile.age,
            height=profile.height,
            weight=float(profile.weight) if profile.weight else None,
        )


@profiles_router.put("/update/{user_id}", status_code=status.HTTP_200_OK)
async def update_profile(user_id: int, updated_profile: Profiles, database: database_dependency) -> None:
    try:
        update_profile = update(ProfileTable).where(ProfileTable.user_id == user_id).values(  # type: ignore[arg-type]
            {
                ProfileTable.age: updated_profile.age,
                ProfileTable.weight: updated_profile.weight,
                ProfileTable.height: updated_profile.height,
            },
        )
        database.execute(update_profile)
        database.commit()
    except IntegrityError as e:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occurred while updating profile",
        ) from e
