from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TransportationBase(BaseModel):
    type: str # 'bus', 'metro', 'car', 'walking', 'cycling'
    distance_km: float

class TransportationCreate(TransportationBase):
    pass

class Transportation(TransportationBase):
    id: int
    user_id: int
    eco_points_earned: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    eco_points: int
    eco_score: float
    transportations: List[Transportation] = []

    class Config:
        from_attributes = True
