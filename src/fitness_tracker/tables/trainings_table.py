from sqlalchemy import Column, Date, ForeignKey, Integer, String

from fitness_tracker.database import Base


class TrainingsTable(Base):
    __tablename__ = "trainings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
