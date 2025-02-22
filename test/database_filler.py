from sqlalchemy.orm import Session

from fitness_tracker.tables.exercise_table import ExerciseTable

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


def fill_database(db_session: Session) -> None:
    for exercise_dict in EXERCISES:
        exercise_record = ExerciseTable(
            exercise_name=exercise_dict["exercise_name"],
            muscle_group=exercise_dict["muscle_group"],
        )
        db_session.add(exercise_record)
    db_session.commit()
