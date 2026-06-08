import { useLocation, Link } from 'react-router-dom';
import { Target, TrendingUp, Zap, Navigation, Utensils, Droplet, AlertTriangle, CheckCircle2, Award, CloudLightning, Shield, ChevronRight } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { calculateEcoPoints, calculateCarbonFootprint, getAchievements } from '../utils/calculations';
import { auth } from '../utils/auth';
import DataVerificationCard from '../components/DataVerificationCard';

export default function Dashboard() {
  const location = useLocation();
  const user = auth.getCurrentUser();
  const { newScore, message, assessmentData } = location.state || {};

  const data = user?.lastAssessment?.data || assessmentData || {
    busTrips: '0', metroTrips: '0', personalVehicleDays: '0',
    walkingSteps: '0', cyclingMinutes: '0', electricityUnits: '0',
    vegetarianDays: '0', nonVegetarianMeals: '0', waterBottles: '0'
  };

  const hasData = !!assessmentData || !!user?.lastAssessment;
  const ecoPoints = user?.ecoPoints || (calculateEcoPoints(data) + (hasData ? 0 : 50));
  const carbonData = calculateCarbonFootprint(data);
  const achievements = getAchievements(data, ecoPoints).filter(a => a.unlocked);
  const finalScore = newScore !== undefined ? newScore : (user?.ecoScore || 50);
  const carbonReduction = Math.min(100, Math.max(0, (finalScore * 0.6) - 10)).toFixed(1);

  let level = "Eco Learner";
  let levelColor = "text-yellow-400";
  if (finalScore >= 80) { level = "Green Champion"; levelColor = "text-green-400"; }
  else if (finalScore >= 60) { level = "Eco Warrior"; levelColor = "text-primary-400"; }

  const recommendations = [];
  if (Number(data.personalVehicleDays) > 15) {
    recommendations.push({ type: 'warning', icon: <Navigation size={20} />, title: "High Vehicle Usage", desc: "Consider using metro, bus, cycling, or walking to reduce emissions." });
  }
  if (Number(data.electricityUnits) > 200) {
    recommendations.push({ type: 'warning', icon: <Zap size={20} />, title: "High Electricity Consumption", desc: "Recommend reducing AC usage, using LED lights, and switching off unused appliances." });
  }
  if (Number(data.nonVegetarianMeals) > 4) {
    recommendations.push({ type: 'warning', icon: <Utensils size={20} />, title: "High Meat Consumption", desc: "Suggest protein-rich vegetarian alternatives such as lentils, paneer, soybeans, chickpeas, and nuts." });
  }
  if (Number(data.waterBottles) > 5) {
    recommendations.push({ type: 'warning', icon: <Droplet size={20} />, title: "High Plastic Waste", desc: "Recommend carrying a reusable water bottle." });
  }
  if (Number(data.walkingSteps) >= 10000) {
    recommendations.push({ type: 'success', icon: <CheckCircle2 size={20} />, title: "Excellent Activity Level!", desc: "Congratulations! You hit over 10,000 steps! You've been awarded +20 Eco Points." });
  }
  if (hasData && recommendations.length === 0) {
    recommendations.push({ type: 'success', icon: <CheckCircle2 size={20} />, title: "Great Job!", desc: "Your habits are looking great! Keep up the sustainable lifestyle." });
  }

  return (
    <div className="min-h-screen w-full bg-background pt-24 px-4 md:px-8 pb-12">
      <div className="max-w-7xl mx-auto space-y-8 animate-fade-in">
        {message && (
          <div className="p-4 rounded-xl bg-primary-500/10 text-primary-400 border border-primary-500/20 flex items-center gap-3 animate-slide-up">
            <CheckCircle2 size={20} />
            <p className="font-medium">{message}</p>
          </div>
        )}

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-3xl font-bold">Sustainability Dashboard</h2>
            <p className="text-gray-400">Your personalized environmental impact overview.</p>
          </div>
          {!hasData && (
            <Link to="/assessment" className="btn-primary py-2 text-sm px-4 w-full md:w-auto justify-center">
              Take Assessment
            </Link>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass-card p-6 border-primary-500/30 flex flex-col items-center justify-center text-center relative overflow-hidden group">
            <div className="w-10 h-10 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center mb-3 relative z-10">
              <Target size={20} />
            </div>
            <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-1">Eco Score</h3>
            <div className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-emerald-200">
              {finalScore}
            </div>
          </div>

          <Link to="/rewards" className="glass-card p-6 flex flex-col items-center justify-center text-center relative overflow-hidden group hover:border-yellow-500/50 transition-colors cursor-pointer">
            <div className="w-10 h-10 rounded-full bg-yellow-500/20 text-yellow-400 flex items-center justify-center mb-3 relative z-10">
              <Award size={20} />
            </div>
            <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-1">Eco Points</h3>
            <div className="text-4xl font-bold text-yellow-400 flex items-baseline gap-1">
              {ecoPoints} <span className="text-sm font-medium text-gray-500">pts</span>
            </div>
          </Link>

          <div className="glass-card p-6 flex flex-col items-center justify-center text-center relative overflow-hidden group">
            <div className="w-10 h-10 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center mb-3 relative z-10">
              <TrendingUp size={20} />
            </div>
            <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-1">Level</h3>
            <div className={`text-2xl font-bold mt-1 ${levelColor}`}>{level}</div>
          </div>

          <div className="glass-card p-6 flex flex-col items-center justify-center text-center relative overflow-hidden group">
            <div className="w-10 h-10 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center mb-3 relative z-10">
              <CloudLightning size={20} />
            </div>
            <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-1">Est. Reduction</h3>
            <div className="text-3xl font-bold mt-1 text-cyan-400">{carbonReduction}%</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 flex flex-col">
            <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
              <Target size={20} className="text-primary-400" />
              Carbon Footprint Overview
            </h3>
            <p className="text-gray-400 text-sm mb-6">Estimated CO₂e generated per month.</p>
            <div className="flex-1 flex flex-col sm:flex-row items-center justify-center">
              <div className="w-full sm:w-1/2 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={carbonData.categories} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                      {carbonData.categories.map((entry, index) => (<Cell key={`cell-${index}`} fill={entry.fill} />))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} itemStyle={{ color: '#fff' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="w-full sm:w-1/2 space-y-4">
                <div className="text-center sm:text-left mb-6">
                  <div className="text-4xl font-bold">{carbonData.total} <span className="text-lg text-gray-500">kg</span></div>
                  <div className="text-sm text-gray-400">Total Emissions</div>
                </div>
                <div className="space-y-3">
                  {carbonData.categories.map((c, i) => (
                    <div key={i} className="flex justify-between items-center text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: c.fill }}></div>
                        <span>{c.name}</span>
                      </div>
                      <span className="font-semibold">{c.value} kg</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="glass-card p-6 flex flex-col border-primary-500/20">
            <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Zap size={20} className="text-primary-400" />
              AI Sustainability Coach
            </h3>
            <div className="flex-1 space-y-4">
              {!hasData ? (
                <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4 py-8">
                  <AlertTriangle size={40} className="opacity-50" />
                  <p>Take the sustainability assessment to get personalized insights.</p>
                </div>
              ) : (
                recommendations.map((rec, i) => (
                  <div key={i} className={`p-4 rounded-xl border flex gap-4 ${rec.type === 'warning' ? 'bg-red-500/10 border-red-500/20 text-red-400' : 'bg-primary-500/10 border-primary-500/20 text-primary-400'}`}>
                    <div className="shrink-0 mt-1">{rec.icon}</div>
                    <div>
                      <h4 className="font-semibold mb-1 text-white">{rec.title}</h4>
                      <p className={`text-sm ${rec.type === 'warning' ? 'text-red-200' : 'text-primary-200'}`}>{rec.desc}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold flex items-center gap-2">
                <Shield size={20} className="text-primary-400" />
                Recent Achievements
              </h3>
              <Link to="/rewards" className="text-sm text-primary-400 hover:text-primary-300 flex items-center">
                View All <ChevronRight size={16} />
              </Link>
            </div>
            {achievements.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {achievements.slice(0, 4).map(badge => (
                  <div key={badge.id} className="p-3 rounded-xl bg-black/20 border border-primary-500/20 flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-emerald-600 flex items-center justify-center text-white shrink-0">
                      <Award size={20} />
                    </div>
                    <div>
                      <div className="font-bold text-sm text-white">{badge.name}</div>
                      <div className="text-xs text-primary-300">Unlocked!</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500 bg-black/20 rounded-xl border border-white/5">
                No achievements unlocked yet. Keep tracking!
              </div>
            )}
          </div>

          <div className="glass-card p-6 flex flex-col justify-center items-center text-center bg-gradient-to-br from-surface to-primary-900/20">
            <div className="w-16 h-16 rounded-full bg-yellow-500/20 text-yellow-400 flex items-center justify-center mb-4">
              <Award size={32} />
            </div>
            <h3 className="text-2xl font-bold mb-2">Reward Center</h3>
            <p className="text-gray-400 mb-6 max-w-sm">
              You have <strong className="text-yellow-400">{ecoPoints} points</strong> available. Redeem them for metro recharges and transport credits!
            </p>
            <Link to="/rewards" className="btn-primary w-full sm:w-auto justify-center">
              Browse Rewards
            </Link>
          </div>
        </div>

        {/* Data Verification Card */}
        <DataVerificationCard />
      </div>
    </div>
  );
}
