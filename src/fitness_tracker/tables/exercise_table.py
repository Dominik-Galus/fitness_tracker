from sqlalchemy import Column, Integer, String

from fitness_tracker.database import Base


class ExerciseTable(Base):
    __tablename__ = "exercise"
    id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String, nullable=False, unique=True)
    muscle_group = Column(String, nullable=False)
