from collections.abc import Generator
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, desc, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from fitness_tracker.configs.sorting_communication import ASCENDING, BY_DATE, BY_NAME, DESCENDING
from fitness_tracker.database import SessionLocal
from fitness_tracker.models.exercise_set import ExerciseSet
from fitness_tracker.models.training import Training
from fitness_tracker.models.training_request import TrainingRequest
from fitness_tracker.tables.exercise_table import ExerciseTable
from fitness_tracker.tables.sets_table import SetsTable
from fitness_tracker.tables.trainings_table import TrainingsTable

trainings_router = APIRouter(prefix="/trainings", tags=["trainings"])
SORT_BY: set[str] = {BY_NAME, BY_DATE}
ORDER_BY: set[str] = {DESCENDING, ASCENDING}


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
    training: TrainingRequest,
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


@trainings_router.get("/fetch/sorted/{user_id}")
async def get_sorted_trainings(
    user_id: int,
    sort_by: str,
    order: str,
    database: database_dependency,
    offset: int = 0,
) -> list[Training] | None:
    try:
        sort_by = sort_by.lower()
        order = order.lower()

        if sort_by not in SORT_BY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot sort by: {sort_by}.",
            )
        if order not in ORDER_BY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot order by: {order}.",
            )

        sorted_results: list[Training] = []
        trainings = database.query(TrainingsTable).filter(
            TrainingsTable.user_id == user_id,
        )
        if not trainings:
            return None

        trainings = trainings.order_by(desc(sort_by)) if order == DESCENDING else trainings.order_by(sort_by)
        sorted_trainings = trainings.offset(offset).limit(5).all()

        for training in sorted_trainings:
            training_model = Training(training_name=training.name, date=training.date, training_id=training.id)
            sorted_results.append(training_model)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occured while fetchin all trainings.",
        ) from e
    else:
        return sorted_results


@trainings_router.get("/fetch/search")
async def get_trainings_by_characters(
    characters: str,
    user_id: int,
    database: database_dependency,
) -> list[Training] | None:
    try:
        filtered_trainings: list[Training] = []

        trainings = database.query(TrainingsTable).filter(
            TrainingsTable.name.like(f"%{characters}%"),
            TrainingsTable.user_id == user_id,
        ).all()
        if not trainings:
            return None

        for training in trainings:
            training_model = Training(training_name=training.name, date=training.date, training_id=training.id)
            filtered_trainings.append(training_model)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occured while fetchin all trainings.",
        ) from e
    else:
        return filtered_trainings


@trainings_router.get("/details/{training_id}")
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
                set_id=exercise_set.id,
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


@trainings_router.delete("/delete/{training_id}")
async def delete_training(training_id: int, user_id: int, database: database_dependency) -> None:
    try:
        training_statement = delete(TrainingsTable).where(   # type: ignore[arg-type]
            TrainingsTable.id == training_id,
        ).where(TrainingsTable.user_id == user_id)

        database.execute(training_statement)
        database.commit()
    except IntegrityError as e:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occured while fetchin all trainings.",
        ) from e


@trainings_router.put("/update/{training_id}")
async def update_training(
    training_id: int,
    sets: list[ExerciseSet],
    database: database_dependency,
) -> None:
    try:
        all_sets = database.query(SetsTable).filter(SetsTable.training_id == training_id).all()
        if not all_sets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error with processing training with id: {training_id}.",
            )

        sets_id = {exercise_set.set_id for exercise_set in sets}
        deleted_sets = [exercise_set.id for exercise_set in all_sets if exercise_set.id not in sets_id]
        for deleted_set in deleted_sets:
            delete_statement = delete(SetsTable).where(SetsTable.id == deleted_set)  # type: ignore[arg-type]
            database.execute(delete_statement)

        for exercise_set in sets:
            if not exercise_set.set_id:
                exercise = database.query(ExerciseTable).filter(
                    ExerciseTable.exercise_name == exercise_set.exercise_name,
                ).first()
                if not exercise:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Error with finding exercise {exercise_set.exercise_name}",
                    )

                set_model = SetsTable(
                    training_id=training_id,
                    exercise_id=exercise.id,
                    repetitions=exercise_set.repetitions,
                    weight=exercise_set.weight,
                )
                database.add(set_model)
                continue

            current_set = update(SetsTable).where(SetsTable.id == exercise_set.set_id).values(  # type: ignore[arg-type]
                {
                    SetsTable.weight: exercise_set.weight,
                    SetsTable.repetitions: exercise_set.repetitions,
                },
            )
            database.execute(current_set)
        database.commit()
    except IntegrityError as e:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occured while updating training.",
        ) from e
