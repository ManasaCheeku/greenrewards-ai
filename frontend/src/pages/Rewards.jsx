import { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Award, Gift, ChevronRight, CheckCircle2, AlertCircle, Shield, Footprints, Droplet, Zap, Leaf } from 'lucide-react';
import { calculateEcoPoints, getAchievements } from '../utils/calculations';
import { auth } from '../utils/auth';

export default function Rewards() {
  const location = useLocation();
  const user = auth.getCurrentUser();
  const { assessmentData } = location.state || {};

  const data = user?.lastAssessment?.data || assessmentData || {
    busTrips: '0', metroTrips: '0', personalVehicleDays: '0',
    walkingSteps: '0', cyclingMinutes: '0', electricityUnits: '0',
    vegetarianDays: '0', nonVegetarianMeals: '0', waterBottles: '0'
  };

  const initialPoints = user?.ecoPoints || (calculateEcoPoints(data) + 50);
  const [points, setPoints] = useState(initialPoints);
  const [notification, setNotification] = useState(null);
  const achievements = getAchievements(data, points);

  const rewardsList = [
    { id: 1, title: '₹20 Metro Recharge', points: 100, icon: '🚇', color: 'from-blue-500 to-indigo-500' },
    { id: 2, title: '₹50 Transport Credit', points: 250, icon: '🚌', color: 'from-emerald-400 to-teal-500' },
    { id: 3, title: '₹100 Transport Credit', points: 500, icon: '🚆', color: 'from-purple-500 to-fuchsia-500' },
  ];

  const handleRedeem = (reward) => {
    if (points >= reward.points) {
      setPoints(prev => prev - reward.points);
      setNotification({ type: 'success', message: `Successfully redeemed: ${reward.title}!` });
    } else {
      setNotification({ type: 'error', message: `Not enough points for ${reward.title}. You need ${reward.points - points} more.` });
    }
    setTimeout(() => setNotification(null), 3000);
  };

  const getIcon = (name) => {
    switch (name) {
      case 'Footprints': return <Footprints size={24} />;
      case 'Shield': return <Shield size={24} />;
      case 'Droplet': return <Droplet size={24} />;
      case 'Zap': return <Zap size={24} />;
      case 'Leaf': return <Leaf size={24} />;
      default: return <Award size={24} />;
    }
  };

  return (
    <div className="min-h-screen w-full bg-background pt-24 px-4 md:px-8 pb-12">
      <div className="max-w-7xl mx-auto space-y-8 animate-fade-in">
        {notification && (
          <div className={`p-4 rounded-xl border flex items-center gap-3 animate-slide-up ${notification.type === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-400' : 'bg-primary-500/10 border-primary-500/20 text-primary-400'}`}>
            {notification.type === 'error' ? <AlertCircle size={20} /> : <CheckCircle2 size={20} />}
            <p className="font-medium">{notification.message}</p>
          </div>
        )}

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-3xl font-bold">Reward Center</h2>
            <p className="text-gray-400">Redeem your hard-earned Eco Points for real rewards.</p>
          </div>
          <div className="glass-card px-6 py-4 flex items-center gap-4 border-yellow-500/30 shadow-[0_0_15px_rgba(234,179,8,0.1)] w-full md:w-auto">
            <div className="p-2 rounded-full bg-yellow-500/20 text-yellow-400">
              <Award size={24} />
            </div>
            <div>
              <div className="text-sm text-yellow-400/80 font-bold uppercase tracking-wider">Balance</div>
              <div className="text-3xl font-bold text-yellow-400">{points} <span className="text-lg">pts</span></div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <Gift className="text-primary-400" size={20} />
              Available Rewards
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {rewardsList.map(reward => (
                <div key={reward.id} className="glass-card overflow-hidden group">
                  <div className={`h-24 bg-gradient-to-r ${reward.color} flex items-center justify-center text-4xl shadow-inner relative`}>
                    <div className="absolute inset-0 bg-black/10"></div>
                    <span className="relative z-10 drop-shadow-md">{reward.icon}</span>
                  </div>
                  <div className="p-6">
                    <h4 className="font-bold text-lg mb-1">{reward.title}</h4>
                    <p className="text-yellow-400 font-semibold mb-6 flex items-center gap-1.5">
                      <Award size={16} /> {reward.points} Points
                    </p>
                    <button
                      onClick={() => handleRedeem(reward)}
                      className={`w-full py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
                        points >= reward.points
                          ? 'bg-white/10 hover:bg-primary-500 text-white hover:shadow-lg hover:shadow-primary-500/30'
                          : 'bg-black/30 text-gray-500 cursor-not-allowed border border-white/5'
                      }`}
                    >
                      {points >= reward.points ? 'Redeem Now' : 'Not Enough Points'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-6">
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <Shield className="text-primary-400" size={20} />
              Your Badges
            </h3>
            <div className="glass-card p-6 flex flex-col gap-4">
              {achievements.map(badge => (
                <div
                  key={badge.id}
                  className={`p-4 rounded-xl border flex items-center gap-4 transition-all duration-300 ${
                    badge.unlocked
                      ? 'bg-primary-500/10 border-primary-500/30'
                      : 'bg-black/20 border-white/5 opacity-60 grayscale'
                  }`}
                >
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 ${
                    badge.unlocked ? 'bg-gradient-to-br from-primary-400 to-emerald-600 text-white shadow-lg shadow-primary-500/20' : 'bg-gray-800 text-gray-500'
                  }`}>
                    {getIcon(badge.icon)}
                  </div>
                  <div>
                    <h4 className={`font-bold ${badge.unlocked ? 'text-white' : 'text-gray-400'}`}>{badge.name}</h4>
                    <p className="text-xs text-gray-400 mt-1">{badge.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
