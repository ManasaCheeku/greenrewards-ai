from typing import Dict
from datetime import datetime
from services import ai_verifier

# Walking module: carbon calculation and AI verification utilities

STEP_TO_KM = 1.0 / 1300.0
CAR_EMISSION_KG_PER_KM = 0.2


def estimate_distance_from_steps(steps: int) -> float:
    return steps * STEP_TO_KM


def estimate_carbon_saved(distance_km: float) -> float:
    return distance_km * CAR_EMISSION_KG_PER_KM


def generate_walking_insights(user_stats: Dict) -> Dict:
    # Produce simple textual insights
    insights = []
    total_km = user_stats.get('total_distance_km', 0.0)
    total_carbon = user_stats.get('total_carbon_saved_kg', 0.0)
    if total_km > 0:
        insights.append(f"You walked {total_km:.1f} km and avoided approximately {total_carbon:.2f} kg CO₂ emissions.")
    if user_stats.get('walking_streak_days', 0) >= 7:
        insights.append("Great streak! Keep it up to earn the 7-day walking streak bonus.")
    if user_stats.get('green_points', 0) < 50:
        insights.append("You're close to earning the Green Walker badge. Keep walking!")
    return {"insights": insights}


def ai_verify_screenshot(file_path: str) -> float:
    # Use ai_verifier to do a light verification; return confidence 0.0-1.0
    try:
        res = ai_verifier.verify_proof(file_path, proof_type='travel')
        return float(res.get('confidence', 0.0))
    except Exception:
        return 0.0
