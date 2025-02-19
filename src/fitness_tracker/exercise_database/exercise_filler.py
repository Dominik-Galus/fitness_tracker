from collections.abc import Generator

import requests
from starlette import status

import fitness_tracker.exercise_database.configs as config
from fitness_tracker.database import SessionLocal
from fitness_tracker.tables.exercise_table import ExerciseTable

MUSCLE_URL: str = "https://wger.de/api/v2/muscle"
EXERCISE_URL: str = "https://wger.de/api/v2/exercise/?language=2"


def fetch_muscles(url: str = MUSCLE_URL) -> dict[int, str]:
    muscle_response = requests.get(url, timeout=10)
    if muscle_response.status_code != status.HTTP_200_OK:
        msg = "Couldn't get muscles response."
        raise requests.exceptions.ConnectionError(msg)

    muscle_data = muscle_response.json()[config.RESULTS]
    return {muscle[config.MUSCLE_ID]: muscle.get(config.LANGUAGE, "Unknown") for muscle in muscle_data}


def fetch_exercises(muscle_map: dict[int, str], url: str = EXERCISE_URL) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}
    while url:
        exercise_response = requests.get(url, timeout=10)
        if exercise_response.status_code != status.HTTP_200_OK:
            break

        exercise_data = exercise_response.json()[config.RESULTS]
        for exercise in exercise_data:
            muscle_names = [muscle_map.get(muscle_id, "Unknown") for muscle_id in exercise[config.MUSCLES]]
            muscle_names = [muscle for muscle in muscle_names if muscle and muscle != "Unknown"]

            if muscle_names:
                results[exercise[config.EXERCISE_NAME]] = muscle_names

        url = exercise_response.json()[config.NEXT_PAGE]
    return results


def get_database() -> Generator:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


def main() -> None:
    db = next(get_database())

    muscle_map = fetch_muscles()
    exercises = fetch_exercises(muscle_map)

    for exercise_name, muscle_groups in exercises.items():
        muscle_group_str = ", ".join(muscle_groups)

        exercise_record = ExerciseTable(exercise_name=exercise_name, muscle_group=muscle_group_str)
        db.add(exercise_record)
        db.commit()


if __name__ == "__main__":
    main()
