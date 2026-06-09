from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks, Request
from fastapi.responses import JSONResponse
import json
import os
import shutil
import uuid
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud
from database import SessionLocal, engine
from services import ai_verifier
import auth
from database import SessionLocal
import hashlib
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from services import campaigns as campaign_services
import crud as crud_module
from services import walking as walking_services

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GreenRewards AI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_proof_background(proof_id: int, file_path: str, proof_type: str):
    # Create fresh DB session for background work
    db = SessionLocal()
    try:
        # Run AI verifier (stub) and update DB accordingly
        result = ai_verifier.verify_proof(file_path, proof_type)

        # record a sustainability action entry
        crud.add_sustainability_action(
            db,
            proof_id=proof_id,
            action_type=result.get("detected_action", "unknown"),
            confidence=result.get("confidence", 0.0),
            carbon_saved_kg=result.get("carbon_saved_kg", result.get("estimated_carbon_kg", 0.0)),
        )

        proof = crud.get_proof(db, proof_id)
        if not proof:
            return

        user_id = proof.user_id

        # Domain-specific recording
        pts = int(result.get("points_awarded", 0))
        if proof_type == 'travel':
            mode = result.get('detected_action', 'private')
            distance = float(result.get('distance_km', 0.0) or 0.0)
            carbon_saved = float(result.get('carbon_saved_kg', 0.0) or 0.0)
            crud.create_travel_record(db, user_id=user_id, transport_mode=mode, distance_km=distance, carbon_saved_kg=carbon_saved, points=pts)
            crud.add_carbon_calculation(db, user_id=user_id, source='travel', amount_kg=carbon_saved, confidence=float(result.get('confidence', 0.0)))
        elif proof_type == 'food':
            cls = result.get('detected_action', 'non-vegetarian')
            est_carbon = float(result.get('estimated_carbon_kg', 0.0) or 0.0)
            crud.create_food_receipt(db, user_id=user_id, classification=cls, estimated_carbon_kg=est_carbon, points=pts)
            crud.add_carbon_calculation(db, user_id=user_id, source='food', amount_kg=est_carbon, confidence=float(result.get('confidence', 0.0)))
        elif proof_type == 'waste':
            wtype = result.get('detected_action', 'recycling')
            impact = float(result.get('impact_estimate', 0.0) or 0.0)
            crud.create_waste_record(db, user_id=user_id, waste_type=wtype, impact_estimate=impact, points=pts)
            crud.add_carbon_calculation(db, user_id=user_id, source='waste', amount_kg=impact, confidence=float(result.get('confidence', 0.0)))
        elif proof_type == 'energy':
            consumption = float(result.get('consumption_kwh', 0.0) or 0.0)
            period = result.get('period', '')
            carbon_saved = float(result.get('carbon_saved_kg', 0.0) or 0.0)
            crud.create_energy_record(db, user_id=user_id, consumption_kwh=consumption, period=period, carbon_saved_kg=carbon_saved, remarks=result.get('remarks'))
            crud.add_carbon_calculation(db, user_id=user_id, source='energy', amount_kg=carbon_saved, confidence=float(result.get('confidence', 0.0)))

        # Award points and rewards
        if pts > 0:
            crud.award_reward(db, user_id=user_id, points=pts, reason=f"Verified {proof.proof_type}")

        # compute updated sustainability score and confidence
        crud.compute_sustainability_score(db, user_id)
        crud.compute_carbon_confidence(db, user_id)

        # update proof record
        proof.status = 'verified' if result.get('confidence', 0.0) >= 0.5 else 'rejected'
        proof.ai_result = str(result)
        proof.eco_points_awarded = pts
        db.commit()
    finally:
        db.close()


def process_campaign_proof_background(proof_id: int, file_path: str, proof_type: str, campaign_id: int, participation_id: int):
    db = SessionLocal()
    try:
        result = ai_verifier.verify_proof(file_path, proof_type)

        # record sustainability action
        crud.add_sustainability_action(db, proof_id=proof_id, action_type=result.get("detected_action", "unknown"), confidence=result.get("confidence", 0.0), carbon_saved_kg=result.get("carbon_saved_kg", result.get("estimated_carbon_kg", 0.0)))

        proof = crud.get_proof(db, proof_id)
        if not proof:
            return

        # submit campaign proof linking participation
        carbon = float(result.get('carbon_saved_kg', 0.0) or 0.0)
        pts = int(result.get('points_awarded', 0) or 0)
        crud.submit_campaign_proof(db, campaign_id=campaign_id, participation_id=participation_id, proof_record=proof, carbon_saved_kg=carbon, points_awarded=pts)

        # award points for the proof
        if pts > 0:
            crud.award_reward(db, user_id=proof.user_id, points=pts, reason=f"Campaign {campaign_id} verified proof")

        # update proof record
        proof.status = 'verified' if result.get('confidence', 0.0) >= 0.5 else 'rejected'
        proof.ai_result = str(result)
        proof.eco_points_awarded = pts
        db.commit()
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 60)))
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/transportations/", response_model=schemas.Transportation)
def create_transportation_for_user(
    user_id: int, transportation: schemas.TransportationCreate, db: Session = Depends(get_db)
):
    # Check if user exists
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_transportation(db=db, transportation=transportation, user_id=user_id)


@app.post("/users/{user_id}/proofs/")
async def upload_proof(user_id: int, proof_type: str, file: UploadFile = File(...), background_tasks: BackgroundTasks = None, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    # Validate user
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Authorize: must be the owner or admin
    if current_user.id != user_id and getattr(current_user, 'role', 'employee') != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to upload for this user")

    # Validate file type
    allowed = {"image/png", "image/jpeg", "image/jpg", "application/pdf"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save file securely with size limit and compute hash
    MAX_BYTES = int(os.environ.get('MAX_UPLOAD_BYTES', 5 * 1024 * 1024))  # default 5MB
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="File too large")

    file_hash = hashlib.sha256(content).hexdigest()
    # create filename and write
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = os.path.join(UPLOAD_DIR, filename)
    with open(dest_path, "wb") as buffer:
        buffer.write(content)

    # create DB record
    proof = crud.create_upload_proof(db, user_id=user_id, filename=filename, content_type=file.content_type, proof_type=proof_type, file_hash=file_hash)

    # Run background verification
    if background_tasks is not None:
        background_tasks.add_task(process_proof_background, proof.id, dest_path, proof_type)
    else:
        # synchronous fallback
        process_proof_background(proof.id, dest_path, proof_type, db)

    return JSONResponse({"status": "accepted", "proof_id": proof.id})


@app.get("/users/{user_id}/proofs/", response_model=List[schemas.UploadProof])
def list_user_proofs(user_id: int, db: Session = Depends(get_db)):
    return crud.list_proofs(db, user_id=user_id)


@app.get("/admin/proofs/pending", response_model=List[schemas.UploadProof])
def list_pending_proofs(db: Session = Depends(get_db), _=Depends(auth.require_role('admin'))):
    return db.query(models.UploadProof).filter(models.UploadProof.status == 'pending').all()


@app.post("/admin/proofs/{proof_id}/approve")
def approve_proof(proof_id: int, db: Session = Depends(get_db), admin=Depends(auth.require_role('admin'))):
    proof = crud.get_proof(db, proof_id)
    if not proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    proof.status = 'verified'
    # simple: award points if set
    if proof.eco_points_awarded and proof.eco_points_awarded > 0:
        crud.award_reward(db, user_id=proof.user_id, points=proof.eco_points_awarded, reason="Admin approved proof")
    db.commit()
    return {"status": "approved", "proof_id": proof.id}


@app.post("/admin/proofs/{proof_id}/reject")
def reject_proof(proof_id: int, reason: str = "Rejected by admin", db: Session = Depends(get_db), admin=Depends(auth.require_role('admin'))):
    proof = crud.get_proof(db, proof_id)
    if not proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    proof.status = 'rejected'
    proof.ai_result = (proof.ai_result or '') + f"\nAdmin note: {reason}"
    db.commit()
    return {"status": "rejected", "proof_id": proof.id}


@app.get("/users/{user_id}/dashboard/")
def user_dashboard(user_id: int, db: Session = Depends(get_db)):
    stats = crud.get_dashboard_stats(db, user_id)
    return stats


@app.post("/admin/campaigns/", response_model=schemas.Campaign)
def create_campaign(campaign: schemas.CampaignCreate, db: Session = Depends(get_db), _=Depends(auth.require_role('admin'))):
    c = crud.create_campaign(db, campaign.model_dump())
    return c


@app.post("/admin/campaigns/{campaign_id}/activities", response_model=schemas.CampaignActivity)
def add_campaign_activity(campaign_id: int, activity: dict, db: Session = Depends(get_db), _=Depends(auth.require_role('admin'))):
    act = crud.add_campaign_activity(db, campaign_id=campaign_id, name=activity.get('name'), description=activity.get('description'), activity_type=activity.get('activity_type'), weight=activity.get('weight', 1.0))
    return act


@app.post("/campaigns/{campaign_id}/join")
def join_campaign(campaign_id: int, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    cp = crud.join_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    return {"status": "joined", "participation_id": cp.id}


@app.post("/campaigns/{campaign_id}/proofs/")
async def upload_campaign_proof(campaign_id: int, file: UploadFile = File(...), background_tasks: BackgroundTasks = None, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    # user must be participant
    cp = crud.get_participation(db, campaign_id=campaign_id, user_id=current_user.id)
    if not cp:
        cp = crud.join_campaign(db, campaign_id=campaign_id, user_id=current_user.id)

    # validate file type
    allowed = {"image/png", "image/jpeg", "image/jpg", "application/pdf"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    MAX_BYTES = int(os.environ.get('MAX_UPLOAD_BYTES', 5 * 1024 * 1024))
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="File too large")
    file_hash = hashlib.sha256(content).hexdigest()
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = os.path.join(UPLOAD_DIR, filename)
    with open(dest_path, "wb") as buffer:
        buffer.write(content)

    proof = crud.create_upload_proof(db, user_id=current_user.id, filename=filename, content_type=file.content_type, proof_type="campaign", file_hash=file_hash)

    # background verify and link to campaign
    if background_tasks is not None:
        background_tasks.add_task(process_campaign_proof_background, proof.id, dest_path, "campaign", campaign_id, cp.id)
    else:
        process_campaign_proof_background(proof.id, dest_path, "campaign", campaign_id, cp.id)

    return JSONResponse({"status": "accepted", "proof_id": proof.id, "participation_id": cp.id})


@app.get("/campaigns/{campaign_id}/dashboard/", response_model=schemas.CampaignDashboard)
def campaign_dashboard(campaign_id: int, db: Session = Depends(get_db)):
    d = crud.get_campaign_dashboard(db, campaign_id)
    if not d:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return d


@app.get("/campaigns/{campaign_id}/leaderboard/")
def campaign_leaderboard(campaign_id: int, db: Session = Depends(get_db)):
    rows = crud.get_campaign_leaderboard(db, campaign_id)
    return [{"user_id": r.user_id, "progress": r.progress_value, "completed": r.completed} for r in rows]


@app.get("/campaigns/{campaign_id}/departments/")
def campaign_department_rankings(campaign_id: int, db: Session = Depends(get_db)):
    rows = crud.get_department_rankings(db, campaign_id)
    return [{"department": r[0], "total_progress": float(r[1] or 0.0)} for r in rows]


@app.get("/campaigns/{campaign_id}/tips/")
def campaign_tips(campaign_id: int, db: Session = Depends(get_db)):
    c = crud.get_campaign(db, campaign_id)
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    tips = campaign_services.generate_ai_tips_for_campaign(c)
    return {"tips": tips}


async def parse_walking_submit_request(request: Request):
    content_type = request.headers.get("content-type", "").lower()
    file = None

    if content_type.startswith("multipart/form-data") or content_type.startswith("application/x-www-form-urlencoded"):
        form = await request.form()
        file = form.get("file")
        raw_payload = form.get("payload")

        if raw_payload:
            try:
                data = json.loads(raw_payload) if isinstance(raw_payload, str) else raw_payload
            except json.JSONDecodeError:
                raise HTTPException(status_code=422, detail="Invalid walking payload")
        else:
            data = {
                key: value
                for key, value in {
                    "steps": form.get("steps"),
                    "distance_km": form.get("distance_km"),
                    "purpose": form.get("purpose"),
                    "proof_id": form.get("proof_id"),
                }.items()
                if value not in (None, "")
            }
    else:
        try:
            data = await request.json()
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="Invalid walking payload")

    try:
        payload = schemas.WalkingSubmit.model_validate(data)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    if file is not None and not hasattr(file, "read"):
        file = None

    return payload, file


@app.post("/walking/submit", response_model=schemas.WalkingRecordSchema)
async def walking_submit(request: Request, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    payload, file = await parse_walking_submit_request(request)
    proof_id = None
    if file is not None:
        allowed = {"image/png", "image/jpeg", "image/jpg", "application/pdf"}
        if file.content_type not in allowed:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        content = await file.read()
        MAX_BYTES = int(os.environ.get('MAX_UPLOAD_BYTES', 5 * 1024 * 1024))
        if len(content) > MAX_BYTES:
            raise HTTPException(status_code=400, detail="File too large")
        file_hash = hashlib.sha256(content).hexdigest()
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        dest_path = os.path.join(UPLOAD_DIR, filename)
        with open(dest_path, "wb") as buffer:
            buffer.write(content)
        proof = crud.create_upload_proof(db, user_id=current_user.id, filename=filename, content_type=file.content_type, proof_type='walking', file_hash=file_hash)
        proof_id = proof.id

    distance = payload.distance_km if payload.distance_km is not None else (payload.steps * walking_services.STEP_TO_KM)
    wr = crud.submit_walking_record(db, user_id=current_user.id, steps=payload.steps, distance_km=distance, purpose=payload.purpose, proof_id=proof_id)
    return wr


@app.post("/walking/verify", response_model=schemas.WalkingVerificationSchema)
def walking_verify(walking_id: int, level: str, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    # only admin or verifier role allowed
    if getattr(current_user, 'role', 'employee') not in ('admin', 'verifier'):
        raise HTTPException(status_code=403, detail="Not authorized to verify")
    # If AI verification requested, try to run ai verification on linked proof
    ai_conf = None
    wr = db.query(models.WalkingRecord).filter(models.WalkingRecord.id == walking_id).first()
    if not wr:
        raise HTTPException(status_code=404, detail="Walking record not found")
    if level == 'ai_verified' and wr.proof_id:
        proof = crud.get_proof(db, wr.proof_id)
        if proof:
            # find file
            file_path = os.path.join(UPLOAD_DIR, proof.filename)
            ai_conf = walking_services.ai_verify_screenshot(file_path)

    ver = crud.verify_walking_record(db, walking_id=walking_id, level=level, ai_confidence=ai_conf)
    return ver


@app.get("/walking/stats", response_model=schemas.WalkingStats)
def walking_stats(db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    stats = crud.get_walking_stats(db, current_user.id)
    return stats


@app.get("/walking/rewards")
def walking_rewards(db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    rows = crud.list_walking_rewards(db, current_user.id)
    return rows


@app.get("/walking/carbon-savings")
def walking_carbon_savings(db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    rows = db.query(models.WalkingCarbonSaving).filter(models.WalkingCarbonSaving.user_id == current_user.id).all()
    return [{"amount_kg": r.amount_kg, "walking_id": r.walking_id, "created_at": r.created_at} for r in rows]


@app.get("/users/{user_id}/travel/", response_model=List[schemas.TravelRecord])
def user_travel_records(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_travel_records(db, user_id=user_id, skip=skip, limit=limit)


@app.get("/users/{user_id}/food/", response_model=List[schemas.FoodReceipt])
def user_food_receipts(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_food_receipts(db, user_id=user_id, skip=skip, limit=limit)


@app.get("/users/{user_id}/energy/", response_model=List[schemas.EnergyRecord])
def user_energy_records(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_energy_records(db, user_id=user_id, skip=skip, limit=limit)


@app.get("/users/{user_id}/waste/", response_model=List[schemas.WasteRecord])
def user_waste_records(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_waste_records(db, user_id=user_id, skip=skip, limit=limit)


@app.get("/users/{user_id}/scores/")
def user_scores(user_id: int, db: Session = Depends(get_db)):
    ss = crud.get_latest_sustainability_score(db, user_id)
    cc = crud.get_latest_carbon_confidence(db, user_id)
    return {"sustainability_score": ss and ss.green_impact_score or None, "grade": ss and ss.sustainability_grade or None, "carbon_confidence": cc and cc.confidence_percent or None}

@app.get("/users/{user_id}/transportations/", response_model=List[schemas.Transportation])
def read_transportations(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transportations = crud.get_transportations(db, user_id=user_id, skip=skip, limit=limit)
    return transportations
