from sqlalchemy.orm import Session
import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def calculate_eco_points(transport_type: str, distance_km: float) -> int:
    # Logic for Eco Points based on transport type and distance
    # Walking: +15 points per km
    # Cycling: +10 points per km
    # Metro: +5 points per km
    # Bus: +2 points per km
    # Car: -5 points per km (penalty)
    points_map = {
        "walking": 15,
        "cycling": 10,
        "metro": 5,
        "bus": 2,
        "car": -5
    }
    
    rate = points_map.get(transport_type.lower(), 0)
    return int(rate * distance_km)

def create_transportation(db: Session, transportation: schemas.TransportationCreate, user_id: int):
    points = calculate_eco_points(transportation.type, transportation.distance_km)
    
    db_transportation = models.Transportation(
        **transportation.model_dump(), 
        user_id=user_id,
        eco_points_earned=points
    )
    db.add(db_transportation)
    
    # Update user's total eco points
    user = get_user(db, user_id)
    if user:
        user.eco_points += points
        # Update eco score (simplified logic: base 50 + points/100, max 100)
        user.eco_score = min(100.0, max(0.0, 50.0 + (user.eco_points / 100.0)))
        
    db.commit()
    db.refresh(db_transportation)
    return db_transportation

def get_transportations(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Transportation).filter(models.Transportation.user_id == user_id).offset(skip).limit(limit).all()
