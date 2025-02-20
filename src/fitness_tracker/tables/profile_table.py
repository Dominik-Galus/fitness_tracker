from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer

from fitness_tracker.database import Base


class ProfileTable(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer, CheckConstraint("age > 0"), nullable=False)
    weight = Column(Float, CheckConstraint("weight > 0"), nullable=False)
    height = Column(Integer, CheckConstraint("height > 0"), nullable=False)
