import os
import re
from typing import Dict, Any

# Optional imports; OCR will only run if pytesseract and PIL are available
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False


# Emission factors (kg CO2e per passenger-km) approximate
EMISSION_FACTORS = {
    "private": 0.271,
    "bus": 0.105,
    "metro": 0.068,
    "train": 0.041,
    "ev": 0.07,
    "bicycle": 0.0,
    "walking": 0.0,
}

# Points mapping per event (can be refined)
POINTS_MAP = {
    "walking": 10,
    "bicycle": 15,
    "bus": 8,
    "metro": 10,
    "train": 10,
    "carpool": 6,
    "ev": 5,
    "private": -2,
}


def ocr_extract_text(file_path: str) -> str:
    if not OCR_AVAILABLE:
        return ""
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text or ""
    except Exception:
        return ""


def parse_numbers(text: str):
    nums = re.findall(r"\d+[\.,]?\d*", text)
    try:
        return [float(n.replace(',', '')) for n in nums]
    except Exception:
        return []


def detect_travel(text: str, filename: str) -> Dict[str, Any]:
    combined = (text + " " + filename).lower()
    mode = "private"
    confidence = 0.4
    distance = 0.0

    if any(k in combined for k in ["bus", "ticket", "stagecoach"]):
        mode = "bus"
        confidence = 0.9
    elif any(k in combined for k in ["metro", "subway"]):
        mode = "metro"
        confidence = 0.9
    elif "train" in combined:
        mode = "train"
        confidence = 0.9
    elif any(k in combined for k in ["carpool", "car pool"]):
        mode = "carpool"
        confidence = 0.8
    elif any(k in combined for k in ["ev charging", "ev", "electric vehicle"]):
        mode = "ev"
        confidence = 0.85
    elif any(k in combined for k in ["bike", "bicycle"]):
        mode = "bicycle"
        confidence = 0.95
    elif any(k in combined for k in ["walk", "walking"]):
        mode = "walking"
        confidence = 0.95

    nums = parse_numbers(combined)
    # try to get distance in km from tokens like 'km' or 'km.' near numbers
    km_match = re.search(r"(\d+[\.,]?\d*)\s*km", combined)
    if km_match:
        try:
            distance = float(km_match.group(1).replace(',', ''))
        except Exception:
            distance = nums[0] if nums else 0.0
    else:
        # fallback: use first number as distance if reasonable
        if nums and nums[0] < 1000:
            distance = nums[0]

    return {"mode": mode, "confidence": confidence, "distance_km": float(distance)}


def calculate_travel_carbon_and_points(mode: str, distance_km: float) -> Dict[str, Any]:
    # saved = (private_emission - mode_emission) * distance
    private = EMISSION_FACTORS.get("private", 0.271)
    mode_em = EMISSION_FACTORS.get(mode, private)
    saved = max(0.0, (private - mode_em) * float(distance_km))
    points = POINTS_MAP.get(mode, 0)
    # If private with no distance, treat as single-trip penalty
    if mode == "private" and distance_km == 0:
        saved = 0.0
        points = POINTS_MAP.get("private", -2)
    return {"carbon_saved_kg": round(saved, 3), "points": int(points)}


def detect_food(text: str, filename: str) -> Dict[str, Any]:
    combined = (text + " " + filename).lower()
    confidence = 0.4
    classification = "non-vegetarian"

    if "vegan" in combined:
        classification = "vegan"
        confidence = 0.95
    elif "vegetarian" in combined or "veg" in combined:
        classification = "vegetarian"
        confidence = 0.9
    elif "plant-based" in combined or "plant based" in combined:
        classification = "plant-based"
        confidence = 0.9
    elif "organic" in combined:
        classification = "organic"
        confidence = 0.85
    elif any(k in combined for k in ["beef", "lamb", "pork", "steak"]):
        classification = "high-carbon"
        confidence = 0.9

    # Estimate carbon (kg) per meal rough estimates
    map_carbon = {
        "vegan": 0.5,
        "vegetarian": 1.0,
        "plant-based": 0.8,
        "organic": 0.9,
        "non-vegetarian": 3.0,
        "high-carbon": 5.0,
    }
    points_map = {
        "vegan": 20,
        "vegetarian": 15,
        "plant-based": 12,
        "organic": 10,
        "non-vegetarian": 5,
        "high-carbon": 0,
    }

    est = map_carbon.get(classification, 3.0)
    pts = points_map.get(classification, 0)
    return {"classification": classification, "confidence": float(confidence), "estimated_carbon_kg": float(est), "points": int(pts)}


def detect_waste(text: str, filename: str) -> Dict[str, Any]:
    combined = (text + " " + filename).lower()
    confidence = 0.5
    wtype = "recycling"
    if any(k in combined for k in ["e-waste", "ewaste", "electronics"]):
        wtype = "e-waste"
        confidence = 0.9
    elif any(k in combined for k in ["compost", "composting"]):
        wtype = "compost"
        confidence = 0.9
    elif any(k in combined for k in ["plastic", "bottle", "recycle"]):
        wtype = "plastic"
        confidence = 0.8
    else:
        wtype = "recycling"

    impact_map = {"plastic": 0.5, "paper": 0.2, "e-waste": 1.5, "compost": 0.8, "recycling": 0.4}
    points_map = {"plastic": 4, "paper": 2, "e-waste": 10, "compost": 6, "recycling": 4}

    impact = impact_map.get(wtype, 0.4)
    pts = points_map.get(wtype, 2)
    return {"waste_type": wtype, "confidence": float(confidence), "impact_estimate": float(impact), "points": int(pts)}


def detect_energy(text: str, filename: str) -> Dict[str, Any]:
    combined = (text + " " + filename).lower()
    nums = parse_numbers(combined)
    confidence = 0.5
    consumption = 0.0
    period = ""
    if nums:
        # assume the largest plausible number as kWh
        consumption = max(nums)
        confidence = 0.8
        # try to extract month/year
        m = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{2,4}", combined)
        if m:
            period = m.group(0)
    return {"consumption_kwh": float(consumption), "confidence": float(confidence), "period": period}


def verify_proof(file_path: str, proof_type: str) -> Dict:
    text = ocr_extract_text(file_path)
    filename = os.path.basename(file_path)

    result: Dict[str, Any] = {"domain": proof_type, "raw_text": text, "filename": filename}

    if proof_type == "travel":
        t = detect_travel(text, filename)
        calc = calculate_travel_carbon_and_points(t["mode"], t["distance_km"])
        result.update({
            "detected_action": t["mode"],
            "confidence": t["confidence"],
            "distance_km": t["distance_km"],
            "carbon_saved_kg": calc["carbon_saved_kg"],
            "points_awarded": calc["points"],
            "remarks": "Travel auto-classified",
        })
    elif proof_type == "food":
        f = detect_food(text, filename)
        result.update({
            "detected_action": f["classification"],
            "confidence": f["confidence"],
            "estimated_carbon_kg": f["estimated_carbon_kg"],
            "points_awarded": f["points"],
            "remarks": "Food auto-classified",
        })
    elif proof_type == "waste":
        w = detect_waste(text, filename)
        result.update({
            "detected_action": w["waste_type"],
            "confidence": w["confidence"],
            "impact_estimate": w["impact_estimate"],
            "points_awarded": w["points"],
            "remarks": "Waste auto-classified",
        })
    elif proof_type == "energy":
        e = detect_energy(text, filename)
        # simple carbon calc: assume 0.85 kg CO2 per kWh (region dependent)
        carbon_per_kwh = float(os.environ.get("CARBON_PER_KWH", 0.85))
        carbon_saved = 0.0
        # If consumption is present, we estimate saving as placeholder (to be compared with previous records elsewhere)
        if e.get("consumption_kwh", 0.0) > 0:
            carbon_saved = e["consumption_kwh"] * carbon_per_kwh
        result.update({
            "detected_action": "energy_bill",
            "confidence": e["confidence"],
            "consumption_kwh": e["consumption_kwh"],
            "period": e.get("period", ""),
            "carbon_saved_kg": round(carbon_saved, 3),
            "points_awarded": int(max(0, carbon_saved // 10)),
            "remarks": "Energy usage extracted",
        })
    else:
        result.update({"detected_action": "unknown", "confidence": 0.3, "remarks": "Unknown proof type"})

    return result
