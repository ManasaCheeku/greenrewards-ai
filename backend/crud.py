from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    # Fallback simple context using bcrypt if passlib is not installed in the environment
    import bcrypt
    class _SimpleCryptContext:
        def __init__(self):
            pass
        def hash(self, password: str) -> str:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        def verify(self, plain_password: str, hashed: str) -> bool:
            try:
                if isinstance(hashed, str):
                    hashed_b = hashed.encode('utf-8')
                else:
                    hashed_b = hashed
                return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_b)
            except Exception:
                return False
    pwd_context = _SimpleCryptContext()

import os
from uuid import uuid4
from datetime import datetime

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = pwd_context.hash(user.password) if getattr(user, 'password', None) else None
    db_user = models.User(username=user.username, password_hash=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_password(plain_password, hashed_password):
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

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


def create_upload_proof(db: Session, user_id: int, filename: str, content_type: str, proof_type: str, file_hash: str = None):
    # Check duplicate by file_hash
    if file_hash:
        existing = db.query(models.UploadProof).filter(models.UploadProof.file_hash == file_hash).first()
        if existing:
            return existing

    proof = models.UploadProof(
        user_id=user_id,
        filename=filename,
        content_type=content_type,
        file_hash=file_hash,
        proof_type=proof_type,
        status="pending",
    )
    db.add(proof)
    db.commit()
    db.refresh(proof)
    return proof


def get_proof(db: Session, proof_id: int):
    return db.query(models.UploadProof).filter(models.UploadProof.id == proof_id).first()


def list_proofs(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.UploadProof).filter(models.UploadProof.user_id == user_id).offset(skip).limit(limit).all()


def add_sustainability_action(db: Session, proof_id: int, action_type: str, confidence: float, carbon_saved_kg: float):
    action = models.SustainabilityAction(
        proof_id=proof_id,
        action_type=action_type,
        confidence=confidence,
        carbon_saved_kg=carbon_saved_kg,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def add_carbon_saving(db: Session, user_id: int, amount_kg: float, source: str):
    cs = models.CarbonSaving(user_id=user_id, amount_kg=amount_kg, source=source)
    db.add(cs)
    # update user's eco points (simple conversion: 1 kg -> 1 point)
    user = get_user(db, user_id)
    if user:
        user.eco_points += int(amount_kg)
        user.eco_score = min(100.0, max(0.0, 50.0 + (user.eco_points / 100.0)))
    db.commit()
    db.refresh(cs)
    return cs


def award_reward(db: Session, user_id: int, points: int, reason: str = ""):
    reward = models.Reward(user_id=user_id, points=points, reason=reason)
    db.add(reward)
    user = get_user(db, user_id)
    if user:
        user.eco_points += points
        user.eco_score = min(100.0, max(0.0, 50.0 + (user.eco_points / 100.0)))
    db.commit()
    db.refresh(reward)
    return reward


def create_travel_record(db: Session, user_id: int, transport_mode: str, distance_km: float, carbon_saved_kg: float, points: int, date=None):
    tr = models.TravelRecord(user_id=user_id, transport_mode=transport_mode, distance_km=distance_km, carbon_saved_kg=carbon_saved_kg, points=points)
    db.add(tr)
    user = get_user(db, user_id)
    if user:
        user.eco_points += points
        user.eco_score = min(100.0, max(0.0, 50.0 + (user.eco_points / 100.0)))
    db.commit()
    db.refresh(tr)
    return tr


def create_food_receipt(db: Session, user_id: int, classification: str, estimated_carbon_kg: float, points: int):
    fr = models.FoodReceipt(user_id=user_id, classification=classification, estimated_carbon_kg=estimated_carbon_kg, points=points)
    db.add(fr)
    user = get_user(db, user_id)
    if user:
        user.eco_points += points
        user.eco_score = min(100.0, max(0.0, 50.0 + (user.eco_points / 100.0)))
    db.commit()
    db.refresh(fr)
    return fr


def create_energy_record(db: Session, user_id: int, consumption_kwh: float, period: str, carbon_saved_kg: float, remarks: str = None):
    er = models.EnergyRecord(user_id=user_id, consumption_kwh=consumption_kwh, period=period, carbon_saved_kg=carbon_saved_kg, remarks=remarks)
    db.add(er)
    db.commit()
    db.refresh(er)
    return er


def create_waste_record(db: Session, user_id: int, waste_type: str, impact_estimate: float, points: int):
    wr = models.WasteRecord(user_id=user_id, waste_type=waste_type, impact_estimate=impact_estimate, points=points)
    db.add(wr)
    user = get_user(db, user_id)
    if user:
        user.eco_points += points
        user.eco_score = min(100.0, max(0.0, 50.0 + (user.eco_points / 100.0)))
    db.commit()
    db.refresh(wr)
    return wr


def add_carbon_calculation(db: Session, user_id: int, source: str, amount_kg: float, confidence: float):
    cc = models.CarbonCalculation(user_id=user_id, source=source, amount_kg=amount_kg, confidence=confidence)
    db.add(cc)
    db.commit()
    db.refresh(cc)
    return cc


def compute_sustainability_score(db: Session, user_id: int):
    # Simple scoring heuristic that aggregates points and carbon savings
    user = get_user(db, user_id)
    if not user:
        return None
    total_points = user.eco_points
    total_carbon = db.query(func.coalesce(func.sum(models.CarbonCalculation.amount_kg), 0.0)).filter(models.CarbonCalculation.user_id == user_id).scalar() or 0.0
    # Green impact score: base 50 + normalized points and carbon savings
    score = min(100.0, max(0.0, 50.0 + (total_points / 10.0) + (total_carbon / 10.0)))
    # Grade mapping
    grade = 'F'
    if score >= 90:
        grade = 'A'
    elif score >= 75:
        grade = 'B'
    elif score >= 60:
        grade = 'C'
    elif score >= 45:
        grade = 'D'

    ss = models.SustainabilityScore(user_id=user_id, green_impact_score=score, sustainability_grade=grade)
    db.add(ss)
    db.commit()
    db.refresh(ss)
    return ss


def compute_carbon_confidence(db: Session, user_id: int):
    # Heuristic: average of carbon calculation confidences, weighted by source
    rows = db.query(models.CarbonCalculation).filter(models.CarbonCalculation.user_id == user_id).all()
    if not rows:
        confidence = 50.0
    else:
        avg = sum([r.confidence for r in rows]) / len(rows)
        confidence = min(100.0, max(0.0, avg * 100.0))
    ccs = models.CarbonConfidenceScore(user_id=user_id, confidence_percent=confidence)
    db.add(ccs)
    db.commit()
    db.refresh(ccs)
    return ccs


def get_travel_records(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.TravelRecord).filter(models.TravelRecord.user_id == user_id).offset(skip).limit(limit).all()


def get_food_receipts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.FoodReceipt).filter(models.FoodReceipt.user_id == user_id).offset(skip).limit(limit).all()


def get_energy_records(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.EnergyRecord).filter(models.EnergyRecord.user_id == user_id).offset(skip).limit(limit).all()


def get_waste_records(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.WasteRecord).filter(models.WasteRecord.user_id == user_id).offset(skip).limit(limit).all()


def get_latest_sustainability_score(db: Session, user_id: int):
    return db.query(models.SustainabilityScore).filter(models.SustainabilityScore.user_id == user_id).order_by(models.SustainabilityScore.created_at.desc()).first()


def get_latest_carbon_confidence(db: Session, user_id: int):
    return db.query(models.CarbonConfidenceScore).filter(models.CarbonConfidenceScore.user_id == user_id).order_by(models.CarbonConfidenceScore.created_at.desc()).first()


def get_dashboard_stats(db: Session, user_id: int):
    total_carbon = db.query(models.CarbonSaving).filter(models.CarbonSaving.user_id == user_id).with_entities(func.coalesce(func.sum(models.CarbonSaving.amount_kg), 0.0)).scalar()
    total_actions = db.query(models.SustainabilityAction).join(models.UploadProof).filter(models.UploadProof.user_id == user_id).count()
    user = get_user(db, user_id)
    points = user.eco_points if user else 0
    return {
        "total_carbon_kg": float(total_carbon or 0.0),
        "total_verified_actions": int(total_actions or 0),
        "eco_points": int(points),
    }


### Walking module helpers
STEP_TO_KM = 1.0 / 1300.0  # 1,300 steps = 1 km
CAR_EMISSION_KG_PER_KM = 0.2  # assumed avoided car emissions per km


def submit_walking_record(db: Session, user_id: int, steps: int, distance_km: float = None, purpose: str = None, proof_id: int = None):
    if distance_km is None:
        distance_km = steps * STEP_TO_KM
    wr = models.WalkingRecord(user_id=user_id, steps=steps, distance_km=distance_km, purpose=purpose, proof_id=proof_id)
    db.add(wr)
    db.commit()
    db.refresh(wr)

    # compute carbon savings assuming replacement of private car
    carbon_saved = distance_km * CAR_EMISSION_KG_PER_KM
    add_carbon_saving(db, user_id=user_id, amount_kg=carbon_saved, source='walking')

    # award base points based on steps
    points = 0
    if steps >= 15000:
        points += 30
    elif steps >= 10000:
        points += 20
    elif steps >= 5000:
        points += 10

    # purpose bonuses
    if purpose and 'office' in (purpose or '').lower():
        points += 20
    if purpose and 'vehicle' in (purpose or '').lower():
        points += 15

    if points > 0:
        award_reward(db, user_id=user_id, points=points, reason=f"Walking activity: {steps} steps")
        wr_points = models.WalkingReward(user_id=user_id, walking_id=wr.id, points=points, reason='walking_reward')
        db.add(wr_points)
        db.commit()
        db.refresh(wr_points)

    # update walking carbon saving table
    wcs = models.WalkingCarbonSaving(user_id=user_id, walking_id=wr.id, amount_kg=carbon_saved)
    db.add(wcs)
    db.commit()
    db.refresh(wcs)

    return wr


def verify_walking_record(db: Session, walking_id: int, level: str, ai_confidence: float = None, verifier_notes: str = None):
    # compute confidence mapping
    mapping = {
        'self_reported': 0.5,
        'screenshot': 0.75,
        'ai_verified': 0.9,
        'external': 1.0,
    }
    confidence = mapping.get(level, 0.5)
    if level == 'ai_verified' and ai_confidence is not None:
        # combine confidences (rough heuristic)
        confidence = min(1.0, 0.5 + (ai_confidence * 0.5))

    ver = models.WalkingVerification(walking_id=walking_id, level=level, confidence=confidence, verifier_notes=verifier_notes)
    db.add(ver)
    db.commit()
    db.refresh(ver)

    # update carbon confidence score for user
    walking = db.query(models.WalkingRecord).filter(models.WalkingRecord.id == walking_id).first()
    if walking:
        # compute weighted confidence across walking carbon savings
        add_carbon_calculation(db, user_id=walking.user_id, source='walking_verification', amount_kg=walking.distance_km * CAR_EMISSION_KG_PER_KM, confidence=confidence)
        compute_carbon_confidence(db, walking.user_id)

    return ver


def get_walking_stats(db: Session, user_id: int):
    # totals
    total_steps = db.query(func.coalesce(func.sum(models.WalkingRecord.steps), 0)).filter(models.WalkingRecord.user_id == user_id).scalar() or 0
    total_distance = db.query(func.coalesce(func.sum(models.WalkingRecord.distance_km), 0.0)).filter(models.WalkingRecord.user_id == user_id).scalar() or 0.0
    # daily/weekly/monthly carbon (approx recent ranges)
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    day_start = now - timedelta(days=1)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    daily_carbon = db.query(func.coalesce(func.sum(models.WalkingCarbonSaving.amount_kg), 0.0)).filter(models.WalkingCarbonSaving.user_id == user_id, models.WalkingCarbonSaving.created_at >= day_start).scalar() or 0.0
    weekly_carbon = db.query(func.coalesce(func.sum(models.WalkingCarbonSaving.amount_kg), 0.0)).filter(models.WalkingCarbonSaving.user_id == user_id, models.WalkingCarbonSaving.created_at >= week_start).scalar() or 0.0
    monthly_carbon = db.query(func.coalesce(func.sum(models.WalkingCarbonSaving.amount_kg), 0.0)).filter(models.WalkingCarbonSaving.user_id == user_id, models.WalkingCarbonSaving.created_at >= month_start).scalar() or 0.0
    total_carbon = db.query(func.coalesce(func.sum(models.WalkingCarbonSaving.amount_kg), 0.0)).filter(models.WalkingCarbonSaving.user_id == user_id).scalar() or 0.0

    # streak: count consecutive days with walking records >= 5000 steps
    def compute_streak():
        streak = 0
        for i in range(0, 365):
            check_day = now.date() - timedelta(days=i)
            next_day = check_day + timedelta(days=1)
            cnt = db.query(models.WalkingRecord).filter(models.WalkingRecord.user_id == user_id, models.WalkingRecord.created_at >= datetime.combine(check_day, datetime.min.time()), models.WalkingRecord.created_at < datetime.combine(next_day, datetime.min.time()), models.WalkingRecord.steps >= 5000).count()
            if cnt > 0:
                streak += 1
            else:
                break
        return streak

    streak_days = compute_streak()
    user = get_user(db, user_id)
    points = user.eco_points if user else 0
    # latest carbon confidence
    cc = get_latest_carbon_confidence(db, user_id)

    return {
        'total_steps': int(total_steps),
        'total_distance_km': float(total_distance),
        'daily_carbon_saved_kg': float(daily_carbon),
        'weekly_carbon_saved_kg': float(weekly_carbon),
        'monthly_carbon_saved_kg': float(monthly_carbon),
        'total_carbon_saved_kg': float(total_carbon),
        'green_points': int(points),
        'carbon_confidence': float(cc.confidence_percent if cc else 50.0),
        'walking_streak_days': int(streak_days),
    }


def list_walking_rewards(db: Session, user_id: int):
    return db.query(models.WalkingReward).filter(models.WalkingReward.user_id == user_id).all()


def list_walking_records(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.WalkingRecord).filter(models.WalkingRecord.user_id == user_id).offset(skip).limit(limit).all()


### Campaign CRUD and helpers
def create_campaign(db: Session, campaign: dict):
    c = models.Campaign(
        name=campaign.get('name'),
        slug=campaign.get('slug'),
        description=campaign.get('description'),
        start_date=campaign.get('start_date'),
        end_date=campaign.get('end_date'),
        goal=campaign.get('goal'),
        target_value=campaign.get('target_value'),
        reward_points=campaign.get('reward_points') or 0,
        badge_name=campaign.get('badge_name')
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def get_campaign(db: Session, campaign_id: int):
    return db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()


def list_campaigns(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Campaign).offset(skip).limit(limit).all()


def add_campaign_activity(db: Session, campaign_id: int, name: str, description: str = None, activity_type: str = None, weight: float = 1.0):
    act = models.CampaignActivity(campaign_id=campaign_id, name=name, description=description, activity_type=activity_type, weight=weight)
    db.add(act)
    db.commit()
    db.refresh(act)
    return act


def join_campaign(db: Session, campaign_id: int, user_id: int):
    existing = db.query(models.CampaignParticipation).filter(models.CampaignParticipation.campaign_id == campaign_id, models.CampaignParticipation.user_id == user_id).first()
    if existing:
        return existing
    cp = models.CampaignParticipation(campaign_id=campaign_id, user_id=user_id)
    db.add(cp)
    db.commit()
    db.refresh(cp)
    return cp


def get_participation(db: Session, campaign_id: int, user_id: int):
    return db.query(models.CampaignParticipation).filter(models.CampaignParticipation.campaign_id == campaign_id, models.CampaignParticipation.user_id == user_id).first()


def submit_campaign_proof(db: Session, campaign_id: int, participation_id: int, proof_record: models.UploadProof, carbon_saved_kg: float = 0.0, points_awarded: int = 0):
    cp = models.CampaignProof(campaign_id=campaign_id, participation_id=participation_id, proof_id=proof_record.id, carbon_saved_kg=carbon_saved_kg, points_awarded=points_awarded)
    db.add(cp)
    # update participation progress
    participation = db.query(models.CampaignParticipation).filter(models.CampaignParticipation.id == participation_id).first()
    if participation:
        participation.progress_value = (participation.progress_value or 0.0) + (carbon_saved_kg or 0.0)
        # mark complete if campaign target reached (if target present)
        campaign = get_campaign(db, campaign_id)
        if campaign and campaign.target_value and participation.progress_value >= (campaign.target_value or 0):
            participation.completed = True
            # award reward and badge
            if campaign.reward_points and participation.user_id:
                award_reward(db, user_id=participation.user_id, points=campaign.reward_points, reason=f"Completed campaign {campaign.name}")
                # optionally create badge
                if campaign.badge_name:
                    b = db.query(models.Badge).filter(models.Badge.name == campaign.badge_name).first()
                    if not b:
                        b = models.Badge(name=campaign.badge_name, description=f"Earned for completing {campaign.name}")
                        db.add(b)
    db.commit()
    db.refresh(cp)
    return cp


def get_campaign_leaderboard(db: Session, campaign_id: int, limit: int = 100):
    # rank by progress_value desc
    rows = db.query(models.CampaignParticipation).filter(models.CampaignParticipation.campaign_id == campaign_id).order_by(models.CampaignParticipation.progress_value.desc()).limit(limit).all()
    return rows


def get_department_rankings(db: Session, campaign_id: int):
    # Aggregate by user.department
    from sqlalchemy import func
    q = db.query(models.User.department, func.coalesce(func.sum(models.CampaignParticipation.progress_value), 0)).join(models.CampaignParticipation, models.User.id == models.CampaignParticipation.user_id).filter(models.CampaignParticipation.campaign_id == campaign_id).group_by(models.User.department).order_by(func.sum(models.CampaignParticipation.progress_value).desc()).all()
    return q


def generate_campaign_certificate(db: Session, campaign_id: int, user_id: int, out_dir: str):
    # Simple text certificate generator (placeholder for PDF generation)
    campaign = get_campaign(db, campaign_id)
    user = get_user(db, user_id)
    if not campaign or not user:
        return None
    os.makedirs(out_dir, exist_ok=True)
    fname = f"certificate_{campaign.slug}_{user.username}_{uuid4().hex}.txt"
    path = os.path.join(out_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Certificate of Achievement\n")
        f.write(f"This certifies that {user.username} has completed the campaign: {campaign.name}\n")
        f.write(f"Award: {campaign.reward_points} Green Points\n")
        f.write(f"Issued: {datetime.utcnow().isoformat()}\n")
    cert = models.CampaignCertificate(campaign_id=campaign_id, user_id=user_id, file_path=path)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def get_campaign_dashboard(db: Session, campaign_id: int):
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        return None
    total_participants = db.query(models.CampaignParticipation).filter(models.CampaignParticipation.campaign_id == campaign_id).count()
    total_verified = db.query(models.CampaignProof).filter(models.CampaignProof.campaign_id == campaign_id).count()
    total_carbon = db.query(func.coalesce(func.sum(models.CampaignProof.carbon_saved_kg), 0.0)).filter(models.CampaignProof.campaign_id == campaign_id).scalar() or 0.0
    leaderboard = get_campaign_leaderboard(db, campaign_id, limit=10)
    return {
        "campaign": campaign,
        "total_participants": int(total_participants),
        "total_verified_proofs": int(total_verified),
        "total_carbon_saved_kg": float(total_carbon),
        "leaderboard": leaderboard,
    }

