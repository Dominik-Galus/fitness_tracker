from sqlalchemy.orm import Session

from fitness_tracker.tables.exercise_table import ExerciseTable
from fitness_tracker.tables.profile_table import ProfileTable
from fitness_tracker.tables.sets_table import SetsTable
from fitness_tracker.tables.trainings_table import TrainingsTable
from fitness_tracker.tables.users_table import UsersTable

EXERCISES: list[dict[str, str]] = [
    {
        "exercise_name": "Australian pull-ups",
        "muscle_group": "Shoulders, Biceps, Lats",
    },
    {
        "exercise_name": "Chin-ups",
        "muscle_group": "Lats",
    },
    {
        "exercise_name": "Close-grip Press-ups",
        "muscle_group": "Lats, Chest",
    },
    {
        "exercise_name": "Crunches With Legs Up",
        "muscle_group": "Abs",
    },
    {
        "exercise_name": "Decline Pushups",
        "muscle_group": "Chest",
    },
    {
        "exercise_name": "Barbell Bench Press - NB",
        "muscle_group": "Chest",
    },
    {
        "exercise_name": "Bench Dips On Floor HD",
        "muscle_group": "Biceps, Triceps",
    },
    {
        "exercise_name": "Bench Press",
        "muscle_group": "Chest",
    },
    {
        "exercise_name": "Bench Press Narrow Grip",
        "muscle_group": "Triceps",
    },
    {
        "exercise_name": "Benchpress Dumbbells",
        "muscle_group": "Chest",
    },
]

USERS: list[dict[str, str]] = [
    {"username": "test1", "email": "email1@email.com", "password": "test2"},
    {"username": "test3", "email": "email2@email.com", "password": "test4"},
    {"username": "test5", "email": "email3@email.com", "password": "test6"},
]

PROFILES: list[dict[str, int]] = [
    {"user_id": 1, "age": 15, "weight": 75, "height": 180},
    {"user_id": 2, "age": 18, "weight": 120, "height": 200},
    {"user_id": 3, "age": 35, "weight": 83, "height": 175},
]

TRAININGS: list[tuple[int, dict[str, str], list[dict[str, int]]]] = [
    [
        (1,
            {
                "training_id": 1,
                "training_name": "test1",
                "date": "2025-02-23",
            },
            [
                {
                    "exercise_name": "Australian pull-ups",
                    "repetitions": 12,
                    "weight": 70,
                },
            ],
        ),
        (2,
            {
                "training_id": 2,
                "training_name": "test2",
                "date": "2025-02-23",
            },
            [
                {
                    "exercise_name": "Decline Pushups",
                    "repetitions": 12,
                    "weight": 0,
                },
                {
                    "exercise_name": "Bench Press",
                    "repetitions": 12,
                    "weight": 100,
                },
                {
                    "exercise_name": "Bench Press",
                    "repetitions": 12,
                    "weight": 100,
                },

            ],
        ),
        (2,
            {
                "training_id": 3,
                "training_name": "test3",
                "date": "2025-02-21",
            },
            [
                {
                    "exercise_name": "Decline Pushups",
                    "repetitions": 12,
                    "weight": 0,
                },
                {
                    "exercise_name": "Bench Press",
                    "repetitions": 12,
                    "weight": 100,
                },
                {
                    "exercise_name": "Bench Press",
                    "repetitions": 12,
                    "weight": 100,
                },

            ],
        ),

    ],
]


def fill_database(db_session: Session) -> None:
    for exercise_dict in EXERCISES:
        exercise_record = ExerciseTable(
            exercise_name=exercise_dict["exercise_name"],
            muscle_group=exercise_dict["muscle_group"],
        )
        db_session.add(exercise_record)
    for user_dict in USERS:
        user_record = UsersTable(
            username=user_dict["username"],
            email=user_dict["email"],
            password=user_dict["password"],
        )
        db_session.add(user_record)
    db_session.commit()

    for profile_dict in PROFILES:
        profile_record = ProfileTable(
            user_id=profile_dict["user_id"],
            age=profile_dict["age"],
            weight=profile_dict["weight"],
            height=profile_dict["height"],
        )
        db_session.add(profile_record)
    db_session.commit()

    for training_list in TRAININGS:
        for training_tuple in training_list:
            user_id, training_data, sets = training_tuple
            training_record = TrainingsTable(
                id=training_data["training_id"],
                name=training_data["training_name"],
                date=training_data["date"],
                user_id=user_id,
            )
            db_session.add(training_record)
            db_session.commit()

            for exercise_set in sets:
                exercise = db_session.query(ExerciseTable).filter(
                    ExerciseTable.exercise_name == exercise_set["exercise_name"],
                ).first()
                set_record = SetsTable(
                    training_id=training_data["training_id"],
                    exercise_id=exercise.id,
                    repetitions=exercise_set["repetitions"],
                    weight=exercise_set["weight"],
                )
                db_session.add(set_record)
            db_session.commit()


def fill_users(db_session: Session) -> None:
    for exercise_dict in EXERCISES:
        exercise_record = ExerciseTable(
            exercise_name=exercise_dict["exercise_name"],
            muscle_group=exercise_dict["muscle_group"],
        )
        db_session.add(exercise_record)
    for user_dict in USERS:
        user_record = UsersTable(
            username=user_dict["username"],
            email=user_dict["email"],
            password=user_dict["password"],
        )
        db_session.add(user_record)
    db_session.commit()
