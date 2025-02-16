from sqlalchemy import Column, Float, ForeignKey, Integer

from fitness_tracker.database import Base


class SetsTable(Base):
    __tablename__ = "sets"
    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(Integer, ForeignKey("trainings.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    repetitions = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
