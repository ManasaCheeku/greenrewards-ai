from services import ai_verifier


def test_detect_travel_bus_km():
    text = "Bus ticket distance 12 km"
    res = ai_verifier.detect_travel(text, "ticket.jpg")
    assert res["mode"] == "bus"
    assert res["distance_km"] == 12.0


def test_calculate_travel_carbon_and_points():
    # bus with 10 km
    out = ai_verifier.calculate_travel_carbon_and_points('bus', 10)
    assert 'carbon_saved_kg' in out and out['carbon_saved_kg'] >= 0
    assert out['points'] == ai_verifier.POINTS_MAP['bus']


def test_detect_food_vegan():
    text = "Vegan meal receipt"
    res = ai_verifier.detect_food(text, "receipt.jpg")
    assert res['classification'] == 'vegan'
    assert res['points'] == 20


def test_detect_energy_numbers():
    text = "Total consumption 350 kWh for Jun 2026"
    res = ai_verifier.detect_energy(text, "bill.pdf")
    assert res['consumption_kwh'] >= 350
    assert 'period' in res


def test_detect_waste_ewaste():
    text = "E-waste dropoff receipt"
    res = ai_verifier.detect_waste(text, "ewaste.jpg")
    assert res['waste_type'] == 'e-waste'
    assert res['points'] >= 0
