import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Trophy, Award, TrendingUp, CloudLightning, Shield, Leaf } from 'lucide-react';
import { auth } from '../utils/auth';

export default function Profile() {
  const navigate = useNavigate();
  const user = auth.getCurrentUser();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || ''
  });
  const [memberDays] = useState(() => {
    if (!user?.createdAt) return 0;
    return Math.floor((Date.now() - new Date(user.createdAt).getTime()) / 86400000);
  });

  if (!user) {
    navigate('/login');
    return null;
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    if (formData.name.trim()) {
      auth.updateUser({
        name: formData.name,
        email: formData.email
      });
      setIsEditing(false);
    }
  };

  // Get sustainability level
  let level = "Eco Learner";
  let levelColor = "text-yellow-400";
  if (user.ecoScore >= 80) { level = "Green Champion"; levelColor = "text-green-400"; }
  else if (user.ecoScore >= 60) { level = "Eco Warrior"; levelColor = "text-primary-400"; }

  return (
    <div className="min-h-screen w-full bg-background pt-24 px-4 md:px-8 pb-12">
      <div className="max-w-4xl mx-auto">
        {/* Page Header */}
        <div className="mb-10 space-y-3">
          <h1 className="text-4xl font-bold text-white">Your Profile</h1>
          <p className="text-gray-400">Manage your account and track your progress</p>
        </div>

        {/* Profile Card */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - User Info & Stats */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Information */}
            <div className="glass-card p-8 border-primary-500/20">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white flex items-center gap-3 mb-2">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 to-emerald-600 flex items-center justify-center text-white text-lg font-bold">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    Personal Information
                  </h2>
                  <p className="text-gray-400">Member since {new Date(user.createdAt).toLocaleDateString()}</p>
                </div>
              </div>

              {isEditing ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Full Name</label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      className="glass-input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      disabled
                      className="glass-input w-full opacity-50 cursor-not-allowed"
                    />
                    <p className="text-xs text-gray-400 mt-1">Email cannot be changed</p>
                  </div>
                  <div className="flex gap-3 pt-4">
                    <button
                      onClick={handleSave}
                      className="btn-primary px-6 py-2 text-sm"
                    >
                      Save Changes
                    </button>
                    <button
                      onClick={() => setIsEditing(false)}
                      className="btn-secondary px-6 py-2 text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-4 p-4 bg-black/20 rounded-lg">
                    <User size={20} className="text-primary-400" />
                    <div>
                      <div className="text-xs text-gray-400 uppercase tracking-wider">Full Name</div>
                      <div className="text-lg font-semibold text-white">{user.name}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 p-4 bg-black/20 rounded-lg">
                    <Mail size={20} className="text-primary-400" />
                    <div>
                      <div className="text-xs text-gray-400 uppercase tracking-wider">Email Address</div>
                      <div className="text-lg font-semibold text-white">{user.email}</div>
                    </div>
                  </div>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="btn-secondary w-full py-2 text-sm mt-4"
                  >
                    Edit Profile
                  </button>
                </div>
              )}
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="glass-card p-6 border-primary-500/30">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">Eco Score</div>
                    <div className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-emerald-200">
                      {user.ecoScore}
                    </div>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center">
                    <Trophy size={24} />
                  </div>
                </div>
              </div>

              <div className="glass-card p-6 border-yellow-500/30">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">Eco Points</div>
                    <div className="text-3xl font-bold text-yellow-400">
                      {user.ecoPoints}
                    </div>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-yellow-500/20 text-yellow-400 flex items-center justify-center">
                    <Award size={24} />
                  </div>
                </div>
              </div>

              <div className="glass-card p-6 border-emerald-500/30">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">Level</div>
                    <div className={`text-2xl font-bold ${levelColor}`}>
                      {level}
                    </div>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                    <TrendingUp size={24} />
                  </div>
                </div>
              </div>

              <div className="glass-card p-6 border-cyan-500/30">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">Carbon Reduction</div>
                    <div className="text-2xl font-bold text-cyan-400">
                      {Math.min(100, Math.max(0, (user.ecoScore * 0.6) - 10)).toFixed(1)}%
                    </div>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
                    <CloudLightning size={24} />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Quick Links & Info */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="glass-card p-6 border-white/5">
              <h3 className="text-lg font-semibold mb-4 text-white">Quick Actions</h3>
              <div className="space-y-3">
                <a
                  href="/assessment"
                  className="block px-4 py-3 rounded-lg bg-primary-500/20 hover:bg-primary-500/30 text-primary-400 font-medium transition-colors text-center"
                >
                  Take Assessment
                </a>
                <a
                  href="/dashboard"
                  className="block px-4 py-3 rounded-lg bg-white/5 hover:bg-white/10 text-white font-medium transition-colors text-center"
                >
                  View Dashboard
                </a>
                <a
                  href="/rewards"
                  className="block px-4 py-3 rounded-lg bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 font-medium transition-colors text-center"
                >
                  Redeem Rewards
                </a>
              </div>
            </div>

            {/* Achievements Summary */}
            <div className="glass-card p-6 border-white/5">
              <h3 className="text-lg font-semibold mb-4 text-white flex items-center gap-2">
                <Shield size={20} className="text-primary-400" />
                Achievements
              </h3>
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-primary-500/10 border border-primary-500/20">
                  <div className="flex items-center gap-2 mb-1">
                    <Leaf size={16} className="text-primary-400" />
                    <span className="font-semibold text-sm text-white">Growing Impact</span>
                  </div>
                  <p className="text-xs text-gray-400">Member for {memberDays} days</p>
                </div>
                <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                  <div className="flex items-center gap-2 mb-1">
                    <Award size={16} className="text-blue-400" />
                    <span className="font-semibold text-sm text-white">Total Points</span>
                  </div>
                  <p className="text-xs text-gray-400">{user.ecoPoints} points earned</p>
                </div>
              </div>
              <a
                href="/rewards"
                className="block text-center mt-4 py-2 text-sm font-medium text-primary-400 hover:text-primary-300 transition-colors"
              >
                View All Achievements →
              </a>
            </div>

            {/* Account Info */}
            <div className="glass-card p-6 border-white/5">
              <h3 className="text-lg font-semibold mb-4 text-white">Account Info</h3>
              <div className="space-y-3 text-sm text-gray-400">
                <div>
                  <div className="text-xs uppercase tracking-wider font-medium mb-1">User ID</div>
                  <div className="font-mono text-xs text-gray-500">{user.id}</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wider font-medium mb-1">Member Since</div>
                  <div>{new Date(user.createdAt).toLocaleDateString()}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
