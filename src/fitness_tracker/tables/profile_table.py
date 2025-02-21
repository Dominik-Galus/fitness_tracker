from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer

from fitness_tracker.database import Base


class ProfileTable(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    age = Column(Integer, CheckConstraint("age > 0"), nullable=True)
    weight = Column(Float, CheckConstraint("weight > 0"), nullable=True)
    height = Column(Integer, CheckConstraint("height > 0"), nullable=True)
