from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    eco_points = Column(Integer, default=0)
    eco_score = Column(Float, default=50.0)

    transportations = relationship("Transportation", back_populates="user")


class Transportation(Base):
    __tablename__ = "transportations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, index=True) # bus, metro, car, walking, cycling
    distance_km = Column(Float)
    eco_points_earned = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transportations")
