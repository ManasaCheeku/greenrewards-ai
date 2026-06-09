from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="employee")
    eco_points = Column(Integer, default=0)
    eco_score = Column(Float, default=50.0)
    department = Column(String, nullable=True)

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


class UploadProof(Base):
    __tablename__ = "upload_proofs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    filename = Column(String)
    content_type = Column(String)
    file_hash = Column(String, index=True, nullable=True)
    proof_type = Column(String, index=True)  # travel, food, waste, energy
    status = Column(String, default="pending")  # pending, verified, rejected
    ai_result = Column(String, nullable=True)
    eco_points_awarded = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="upload_proofs")


class SustainabilityAction(Base):
    __tablename__ = "sustainability_actions"

    id = Column(Integer, primary_key=True, index=True)
    proof_id = Column(Integer, ForeignKey("upload_proofs.id"), index=True)
    action_type = Column(String, index=True)  # e.g., bike_ride, vegetarian_meal
    confidence = Column(Float, default=0.0)
    carbon_saved_kg = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    proof = relationship("UploadProof", back_populates="actions")


class CarbonSaving(Base):
    __tablename__ = "carbon_savings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    amount_kg = Column(Float, default=0.0)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="carbon_savings")


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    points = Column(Integer, default=0)
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rewards")


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    period = Column(String, index=True)  # e.g., 2026-06 (month)
    points = Column(Integer, default=0)

    user = relationship("User", back_populates="leaderboard_entries")

# back-populate relations on User and UploadProof
User.upload_proofs = relationship("UploadProof", back_populates="user")
UploadProof.actions = relationship("SustainabilityAction", back_populates="proof")
User.carbon_savings = relationship("CarbonSaving", back_populates="user")
User.rewards = relationship("Reward", back_populates="user")
User.leaderboard_entries = relationship("LeaderboardEntry", back_populates="user")


class TravelRecord(Base):
    __tablename__ = "travel_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    transport_mode = Column(String, index=True)  # bus, metro, train, bicycle, carpool, ev, private
    distance_km = Column(Float, default=0.0)
    carbon_saved_kg = Column(Float, default=0.0)
    points = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="travel_records")


class FoodReceipt(Base):
    __tablename__ = "food_receipts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    classification = Column(String, index=True)  # vegan, vegetarian, plant-based, organic, non-veg
    estimated_carbon_kg = Column(Float, default=0.0)
    points = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="food_receipts")


class EnergyRecord(Base):
    __tablename__ = "energy_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    consumption_kwh = Column(Float, default=0.0)
    period = Column(String, index=True)  # e.g., 2026-06
    carbon_saved_kg = Column(Float, default=0.0)
    remarks = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="energy_records")


class WasteRecord(Base):
    __tablename__ = "waste_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    waste_type = Column(String, index=True)  # plastic, paper, e-waste, compost
    impact_estimate = Column(Float, default=0.0)
    points = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="waste_records")


class CarbonCalculation(Base):
    __tablename__ = "carbon_calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    source = Column(String)
    amount_kg = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="carbon_calculations")


class SustainabilityScore(Base):
    __tablename__ = "sustainability_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    green_impact_score = Column(Float, default=50.0)
    sustainability_grade = Column(String, default="C")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sustainability_scores")


class CarbonConfidenceScore(Base):
    __tablename__ = "carbon_confidence_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    confidence_percent = Column(Float, default=50.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="carbon_confidence_scores")

# back-populate new relations
User.travel_records = relationship("TravelRecord", back_populates="user")
User.food_receipts = relationship("FoodReceipt", back_populates="user")
User.energy_records = relationship("EnergyRecord", back_populates="user")
User.waste_records = relationship("WasteRecord", back_populates="user")
User.carbon_calculations = relationship("CarbonCalculation", back_populates="user")
User.sustainability_scores = relationship("SustainabilityScore", back_populates="user")
User.carbon_confidence_scores = relationship("CarbonConfidenceScore", back_populates="user")


class WalkingRecord(Base):
    __tablename__ = "walking_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    steps = Column(Integer, default=0)
    distance_km = Column(Float, default=0.0)
    purpose = Column(String, nullable=True)
    proof_id = Column(Integer, ForeignKey("upload_proofs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="walking_records")
    proof = relationship("UploadProof")


class WalkingVerification(Base):
    __tablename__ = "walking_verifications"

    id = Column(Integer, primary_key=True, index=True)
    walking_id = Column(Integer, ForeignKey("walking_records.id"), index=True)
    level = Column(String)  # self_reported, screenshot, ai_verified, external
    confidence = Column(Float, default=0.5)
    verifier_notes = Column(String, nullable=True)
    verified_at = Column(DateTime, default=datetime.utcnow)

    walking = relationship("WalkingRecord", backref="verifications")


class WalkingReward(Base):
    __tablename__ = "walking_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    walking_id = Column(Integer, ForeignKey("walking_records.id"), index=True, nullable=True)
    points = Column(Integer, default=0)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="walking_rewards")
    walking = relationship("WalkingRecord", backref="rewards")


class WalkingBadge(Base):
    __tablename__ = "walking_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    badge_name = Column(String)
    description = Column(String, nullable=True)
    awarded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="walking_badges")


class WalkingCarbonSaving(Base):
    __tablename__ = "walking_carbon_savings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    walking_id = Column(Integer, ForeignKey("walking_records.id"), index=True, nullable=True)
    amount_kg = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="walking_carbon_savings")
    walking = relationship("WalkingRecord", backref="carbon_savings")


# back-populate
User.walking_records = relationship("WalkingRecord", back_populates="user")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False)
    slug = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    goal = Column(String, nullable=True)  # e.g., "Walk 50 km in 30 days"
    target_value = Column(Float, nullable=True)  # numeric goal (e.g., 50 km)
    reward_points = Column(Integer, default=0)
    badge_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CampaignActivity(Base):
    __tablename__ = "campaign_activities"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    activity_type = Column(String, nullable=True)  # travel/food/waste/energy/other
    weight = Column(Float, default=1.0)

    campaign = relationship("Campaign", backref="activities")


class CampaignParticipation(Base):
    __tablename__ = "campaign_participations"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    progress_value = Column(Float, default=0.0)
    joined_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)

    user = relationship("User", backref="campaign_participations")
    campaign = relationship("Campaign", backref="participations")


class CampaignProof(Base):
    __tablename__ = "campaign_proofs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True)
    participation_id = Column(Integer, ForeignKey("campaign_participations.id"), index=True)
    proof_id = Column(Integer, ForeignKey("upload_proofs.id"), index=True)
    carbon_saved_kg = Column(Float, default=0.0)
    points_awarded = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", backref="proofs")
    participation = relationship("CampaignParticipation", backref="proofs")
    proof = relationship("UploadProof", backref="campaign_proof")


class CampaignCertificate(Base):
    __tablename__ = "campaign_certificates"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    file_path = Column(String)
    issued_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="campaign_certificates")
    campaign = relationship("Campaign", backref="certificates")
