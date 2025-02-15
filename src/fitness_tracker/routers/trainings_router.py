from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from fitness_tracker.database import SessionLocal
from fitness_tracker.models.exercise_set import ExerciseSet
from fitness_tracker.models.training import Training
from fitness_tracker.tables.exercise_table import ExerciseTable
from fitness_tracker.tables.sets_table import SetsTable
from fitness_tracker.tables.trainings_table import TrainingsTable

trainings_router = APIRouter(prefix="/trainings", tags=["trainings"])


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


database_dependency = Annotated[Session, Depends(get_database)]


@trainings_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_training(
    user_id: int,
    training: Training,
    sets: list[ExerciseSet],
    database: database_dependency,
) -> None:
    try:
        training_model = TrainingsTable(
            user_id=user_id,
            name=training.training_name,
            date=training.date,
        )
        database.add(training_model)
        database.commit()

        for exercise_set in sets:
            exercise = database.query(ExerciseTable).filter(
                ExerciseTable.exercise_name == exercise_set.exercise_name,
            ).first()
            if not exercise:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Exercise {exercise_set.exercise_name} does not exists in database",
                )

            set_model = SetsTable(
                training_id=training_model.id,
                exercise_id=exercise.id,
                repetitions=exercise_set.repetitions,
                weight=exercise_set.weight,
            )
            database.add(set_model)

        database.commit()

    except IntegrityError as e:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occurred while creating training",
        ) from e
