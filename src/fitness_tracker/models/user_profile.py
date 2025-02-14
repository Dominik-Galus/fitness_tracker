from sqlalchemy import Column, Float, ForeignKey, Integer

from fitness_tracker.database import Base


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    age = Column(Integer)
    weight = Column(Float)
    height = Column(Integer)
