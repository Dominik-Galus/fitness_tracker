from collections.abc import Generator
from datetime import date
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
            detail="Error occurred while creating training.",
        ) from e


@trainings_router.get("/fetchall/{user_id}")
async def get_all_trainings(user_id: int, database: database_dependency) -> list[Training] | None:
    try:
        results: list[Training] = []

        trainings = database.query(TrainingsTable).filter(TrainingsTable.user_id == user_id).all()
        if not trainings:
            return None

        for training in trainings:
            training_model = Training(training_name=training.name, date=training.date, training_id=training.id)
            results.append(training_model)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occured while fetchin all trainings.",
        ) from e
    else:
        return results


@trainings_router.get("/fetch/{training_id}")
async def fetch_training_details(
    training_id: int,
    database: database_dependency,
) -> dict[str, list[ExerciseSet] | str | date | None]:
    try:
        training_details: dict[str, list[ExerciseSet] | str | date | None] = {}
        sets_details: list[ExerciseSet] = []

        training = database.query(TrainingsTable).filter(TrainingsTable.id == training_id).first()
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There is no training with id: {training_id}.",
            )

        exercise_sets = database.query(SetsTable).filter(SetsTable.training_id == training_id).all()
        if not exercise_sets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error occurred while getting training details.",
            )

        for exercise_set in exercise_sets:
            exercise = database.query(ExerciseTable).filter(
                ExerciseTable.id == exercise_set.exercise_id,
            ).first()
            if not exercise:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error occurred while fetching exercise",
                )

            set_model = ExerciseSet(
                exercise_name=exercise.exercise_name,
                repetitions=exercise_set.repetitions,
                weight=float(exercise_set.weight),
            )
            sets_details.append(set_model)
        training_details["sets"] = sets_details
        training_details["name"] = training.name
        training_details["date"] = training.date
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occured while fetchin all trainings.",
        ) from e

    else:
        return training_details
