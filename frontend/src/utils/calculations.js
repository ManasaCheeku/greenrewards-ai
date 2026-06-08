// src/utils/calculations.js

export const calculateEcoPoints = (data) => {
  let points = 0;
  
  // Transport
  points += Number(data.busTrips) * 10;
  points += Number(data.metroTrips) * 15;
  
  if (Number(data.cyclingMinutes) > 0) {
    points += 20; // Assume 20 per day/week of cycling, flat for now
  }
  
  if (Number(data.walkingSteps) >= 10000) {
    points += 20;
  }

  // Electricity
  if (Number(data.electricityUnits) > 0 && Number(data.electricityUnits) < 200) {
    points += 50;
  }

  // Plastic
  if (Number(data.waterBottles) <= 1 && data.waterBottles !== '') { // Reusable bottle goal
    points += 30;
  }

  // Food
  if (Number(data.vegetarianDays) >= 5) {
    points += 40;
  }

  return points;
};

export const calculateCarbonFootprint = (data) => {
  // Estimated Carbon Footprint in kg CO2e per month/week depending on how we frame it. 
  // We'll calculate a generic periodic footprint.
  
  // Rules provided:
  // Car = 0.21 kg CO2/km
  // Bus = 0.08 kg CO2/km
  // Metro = 0.04 kg CO2/km
  
  // Assume average trip distances if not provided. (e.g. 10km per trip/day)
  const avgTripDistance = 10; 
  
  const carCarbon = Number(data.personalVehicleDays) * avgTripDistance * 0.21;
  const busCarbon = Number(data.busTrips) * avgTripDistance * 0.08;
  const metroCarbon = Number(data.metroTrips) * avgTripDistance * 0.04;
  const transport = carCarbon + busCarbon + metroCarbon;

  // Electricity: approx 0.85 kg CO2 per kWh depending on grid, let's use 0.5 kg for average
  const electricity = Number(data.electricityUnits) * 0.5;

  // Food: Non-veg meal adds approx 2kg CO2, veg adds 0.5kg
  const food = (Number(data.nonVegetarianMeals) * 2) + (Number(data.vegetarianDays) * 3 * 0.5); // assuming 3 meals/day

  // Plastic: approx 0.08 kg per bottle
  const plastic = Number(data.waterBottles) * 0.08;

  const total = transport + electricity + food + plastic;

  return {
    total: total.toFixed(1),
    categories: [
      { name: 'Transport', value: Number(transport.toFixed(1)), fill: '#3b82f6' }, // blue-500
      { name: 'Electricity', value: Number(electricity.toFixed(1)), fill: '#eab308' }, // yellow-500
      { name: 'Food', value: Number(food.toFixed(1)), fill: '#22c55e' }, // green-500
      { name: 'Plastic', value: Number(plastic.toFixed(1)), fill: '#06b6d4' } // cyan-500
    ]
  };
};

export const getAchievements = (data, points) => {
  const badges = [
    { id: 'green_walker', name: 'Green Walker', icon: 'Footprints', description: 'Walked 10,000+ steps', unlocked: Number(data.walkingSteps) >= 10000 },
    { id: 'eco_warrior', name: 'Eco Warrior', icon: 'Shield', description: 'Earned over 200 Eco Points', unlocked: points >= 200 },
    { id: 'plastic_free', name: 'Plastic-Free Champion', icon: 'Droplet', description: 'Bought 0 water bottles', unlocked: Number(data.waterBottles) === 0 },
    { id: 'energy_saver', name: 'Energy Saver', icon: 'Zap', description: 'Kept electricity under 200 units', unlocked: Number(data.electricityUnits) > 0 && Number(data.electricityUnits) < 200 },
    { id: 'carbon_reducer', name: 'Carbon Reducer', icon: 'Leaf', description: 'Minimized personal vehicle usage', unlocked: Number(data.personalVehicleDays) <= 3 }
  ];
  return badges;
};
