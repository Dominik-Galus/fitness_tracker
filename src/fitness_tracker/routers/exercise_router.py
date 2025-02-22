from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from fitness_tracker.database import SessionLocal
from fitness_tracker.models.exercise import Exercise
from fitness_tracker.tables import ExerciseTable

exercise_router = APIRouter(prefix="/exercise", tags=["exercise"])


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


database_dependency = Annotated[Session, Depends(get_database)]


@exercise_router.get("/search")
async def get_exercises_by_characters(characters: str, database: database_dependency) -> list[Exercise] | None:
    try:
        all_exercises: list[Exercise] = []
        exercises: list[ExerciseTable] | None = database.query(ExerciseTable).filter(
            ExerciseTable.exercise_name.ilike(f"%{characters}%"),
        ).limit(5).all()
        if not exercises:
            return None

        for exercise in exercises:
            exercise_model = Exercise(
                exercise_name=exercise.exercise_name,
                muscle_group=exercise.muscle_group,
            )
            all_exercises.append(exercise_model)
    except IntegrityError as e:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occurred while fetching exercises.",
        ) from e
    else:
        return all_exercises
