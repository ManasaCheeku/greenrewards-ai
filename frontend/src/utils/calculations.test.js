import { describe, it, expect } from 'vitest';
import { calculateEcoPoints, calculateCarbonFootprint, getAchievements } from './calculations';

describe('Sustainability Calculations', () => {
  const mockData = {
    busTrips: '2',
    metroTrips: '1',
    personalVehicleDays: '5',
    walkingSteps: '12000',
    cyclingMinutes: '45',
    electricityUnits: '150',
    vegetarianDays: '6',
    nonVegetarianMeals: '2',
    waterBottles: '0'
  };

  const badHabitsData = {
    busTrips: '0',
    metroTrips: '0',
    personalVehicleDays: '20',
    walkingSteps: '2000',
    cyclingMinutes: '0',
    electricityUnits: '350',
    vegetarianDays: '0',
    nonVegetarianMeals: '15',
    waterBottles: '10'
  };

  it('calculates Eco Points correctly for positive habits', () => {
    const points = calculateEcoPoints(mockData);
    // 2*10(bus) + 1*15(metro) + 20(cycling) + 20(steps>10k) + 50(electricity<200) + 30(bottles<=1) + 40(veg>=5)
    // 20 + 15 + 20 + 20 + 50 + 30 + 40 = 195
    expect(points).toBe(195);
  });

  it('calculates Eco Points correctly for negative habits', () => {
    const points = calculateEcoPoints(badHabitsData);
    // Should be 0 based on rules (no negative points in base logic)
    expect(points).toBe(0);
  });

  it('calculates Carbon Footprint correctly', () => {
    const footprint = calculateCarbonFootprint(mockData);
    // Transport: 5*10*0.21(10.5) + 2*10*0.08(1.6) + 1*10*0.04(0.4) = 12.5
    // Electricity: 150 * 0.5 = 75
    // Food: (2*2) + (6*3*0.5) = 4 + 9 = 13
    // Plastic: 0 * 0.08 = 0
    // Total = 12.5 + 75 + 13 + 0 = 100.5
    expect(footprint.total).toBe("100.5");
    expect(footprint.categories[0].value).toBeCloseTo(12.5); // Transport
    expect(footprint.categories[1].value).toBeCloseTo(75); // Electricity
  });

  it('unlocks badges accurately', () => {
    const badges = getAchievements(mockData, 195);
    
    // Should unlock Green Walker (>10k), Plastic Free (0 bottles), Energy Saver (<200)
    // Won't unlock Eco Warrior (needs 200 pts)
    // Won't unlock Carbon Reducer (needs <= 3 car days)
    
    expect(badges.find(b => b.id === 'green_walker').unlocked).toBe(true);
    expect(badges.find(b => b.id === 'plastic_free').unlocked).toBe(true);
    expect(badges.find(b => b.id === 'energy_saver').unlocked).toBe(true);
    
    expect(badges.find(b => b.id === 'eco_warrior').unlocked).toBe(false);
    expect(badges.find(b => b.id === 'carbon_reducer').unlocked).toBe(false);
  });
});
