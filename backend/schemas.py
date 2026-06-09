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
    password: Optional[str]

class User(UserBase):
    id: int
    eco_points: int
    eco_score: float
    transportations: List[Transportation] = []
    upload_proofs: List["UploadProof"] = []
    rewards: List["Reward"] = []
    role: Optional[str] = "employee"
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True


class UploadProofBase(BaseModel):
    filename: str
    content_type: str
    proof_type: str


class UploadProof(UploadProofBase):
    id: int
    user_id: int
    status: str
    ai_result: Optional[str]
    eco_points_awarded: int
    created_at: datetime

    class Config:
        from_attributes = True


class SustainabilityAction(BaseModel):
    id: int
    proof_id: int
    action_type: str
    confidence: float
    carbon_saved_kg: float
    created_at: datetime

    class Config:
        from_attributes = True


class CarbonSaving(BaseModel):
    id: int
    user_id: int
    amount_kg: float
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class Reward(BaseModel):
    id: int
    user_id: int
    points: int
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TravelRecord(BaseModel):
    id: int
    user_id: int
    transport_mode: str
    distance_km: float
    carbon_saved_kg: float
    points: int
    date: datetime

    class Config:
        from_attributes = True


class FoodReceipt(BaseModel):
    id: int
    user_id: int
    classification: str
    estimated_carbon_kg: float
    points: int
    date: datetime

    class Config:
        from_attributes = True


class EnergyRecord(BaseModel):
    id: int
    user_id: int
    consumption_kwh: float
    period: str
    carbon_saved_kg: float
    remarks: Optional[str]
    date: datetime

    class Config:
        from_attributes = True


class WasteRecord(BaseModel):
    id: int
    user_id: int
    waste_type: str
    impact_estimate: float
    points: int
    date: datetime

    class Config:
        from_attributes = True


class CarbonCalculation(BaseModel):
    id: int
    user_id: int
    source: str
    amount_kg: float
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True


class SustainabilityScore(BaseModel):
    id: int
    user_id: int
    green_impact_score: float
    sustainability_grade: str
    created_at: datetime

    class Config:
        from_attributes = True


class CarbonConfidenceScore(BaseModel):
    id: int
    user_id: int
    confidence_percent: float
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    goal: Optional[str] = None
    target_value: Optional[float] = None
    reward_points: Optional[int] = 0
    badge_name: Optional[str] = None


class Campaign(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    goal: Optional[str]
    target_value: Optional[float]
    reward_points: int
    badge_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignActivity(BaseModel):
    id: int
    campaign_id: int
    name: str
    description: Optional[str]
    activity_type: Optional[str]
    weight: float

    class Config:
        from_attributes = True


class CampaignParticipation(BaseModel):
    id: int
    campaign_id: int
    user_id: int
    progress_value: float
    joined_at: datetime
    completed: bool

    class Config:
        from_attributes = True


class CampaignProof(BaseModel):
    id: int
    campaign_id: int
    participation_id: int
    proof_id: int
    carbon_saved_kg: float
    points_awarded: int
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignCertificate(BaseModel):
    id: int
    campaign_id: int
    user_id: int
    file_path: str
    issued_at: datetime

    class Config:
        from_attributes = True


class CampaignDashboard(BaseModel):
    campaign: Campaign
    total_participants: int
    total_verified_proofs: int
    total_carbon_saved_kg: float
    leaderboard: List[CampaignParticipation] = []

    class Config:
        from_attributes = True


class WalkingSubmit(BaseModel):
    steps: int
    distance_km: Optional[float] = None
    purpose: Optional[str] = "Other"
    proof_id: Optional[int] = None


class WalkingRecordSchema(BaseModel):
    id: int
    user_id: int
    steps: int
    distance_km: float
    purpose: Optional[str]
    proof_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class WalkingVerificationSchema(BaseModel):
    id: int
    walking_id: int
    level: str
    confidence: float
    verifier_notes: Optional[str]
    verified_at: datetime

    class Config:
        from_attributes = True


class WalkingRewardSchema(BaseModel):
    id: int
    user_id: int
    walking_id: Optional[int]
    points: int
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WalkingStats(BaseModel):
    total_steps: int
    total_distance_km: float
    daily_carbon_saved_kg: float
    weekly_carbon_saved_kg: float
    monthly_carbon_saved_kg: float
    total_carbon_saved_kg: float
    green_points: int
    carbon_confidence: float
    walking_streak_days: int

    class Config:
        from_attributes = True
