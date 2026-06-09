import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Bus, Train, Car, Navigation, Bike, AlertCircle, CheckCircle2 } from 'lucide-react';

const USER_ID = 1;

export default function Transportation() {
  const [transportType, setTransportType] = useState('bus');
  const [distance, setDistance] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [ecoPoints, setEcoPoints] = useState(0);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await axios.get(`http://localhost:8000/users/${USER_ID}/transportations/`);
      setHistory(res.data);
    } catch (err) {
      console.log("Error fetching history", err);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadInitialData() {
      try {
        const userRes = await axios.get(`http://localhost:8000/users/${USER_ID}`);
        if (!cancelled) setEcoPoints(userRes.data.eco_points);
      } catch (err) {
        console.log("User not found, you might need to create it first", err);
      }

      try {
        const historyRes = await axios.get(`http://localhost:8000/users/${USER_ID}/transportations/`);
        if (!cancelled) setHistory(historyRes.data);
      } catch (err) {
        console.log("Error fetching history", err);
      }
    }

    loadInitialData();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!distance || isNaN(distance) || Number(distance) <= 0) {
      setStatus({ type: 'error', message: 'Please enter a valid distance.' });
      return;
    }

    setLoading(true);
    setStatus({ type: '', message: '' });

    try {
      const res = await axios.post(`http://localhost:8000/users/${USER_ID}/transportations/`, {
        type: transportType,
        distance_km: Number(distance),
      });
      setStatus({ type: 'success', message: `Great! You earned ${res.data.eco_points_earned} Eco Points!` });
      setEcoPoints(prev => prev + res.data.eco_points_earned);
      setDistance('');
      fetchHistory();
    } catch {
      setStatus({ type: 'error', message: 'Failed to log activity. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const types = [
    { id: 'walking', name: 'Walking', icon: <Navigation size={24} />, rate: '+20 pts/km', color: 'from-green-500 to-emerald-500' },
    { id: 'cycling', name: 'Cycling', icon: <Bike size={24} />, rate: '+15 pts/km', color: 'from-blue-500 to-cyan-500' },
    { id: 'bus', name: 'Bus', icon: <Bus size={24} />, rate: '+10 pts/km', color: 'from-yellow-500 to-orange-500' },
    { id: 'metro', name: 'Metro', icon: <Train size={24} />, rate: '+8 pts/km', color: 'from-purple-500 to-indigo-500' },
    { id: 'car', name: 'Car', icon: <Car size={24} />, rate: '-5 pts/km', color: 'from-red-500 to-pink-500' },
  ];

  return (
    <div className="min-h-screen w-full bg-background pt-24 px-4 md:px-8 pb-12">
      <div className="max-w-7xl mx-auto space-y-6 animate-slide-up">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold mb-2">Transportation Tracker</h2>
            <p className="text-gray-400">Log your daily commute to track your carbon footprint and earn Eco Points.</p>
          </div>
          <div className="glass-card px-6 py-4 flex flex-col items-center border-primary-500/30 shadow-[0_0_15px_rgba(16,185,129,0.2)] w-full md:w-auto">
            <div className="text-sm text-primary-300 font-semibold uppercase tracking-wider mb-1">Your Eco Points</div>
            <div className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200">
              {ecoPoints}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <form onSubmit={handleSubmit} className="glass-card p-8">
              <h3 className="text-xl font-semibold mb-6">Log Activity</h3>

              {status.message && (
                <div className={`p-4 rounded-xl mb-6 flex items-start gap-3 ${status.type === 'error' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-primary-500/10 text-primary-400 border border-primary-500/20'}`}>
                  {status.type === 'error' ? <AlertCircle className="shrink-0 mt-0.5" size={18} /> : <CheckCircle2 className="shrink-0 mt-0.5" size={18} />}
                  <p>{status.message}</p>
                </div>
              )}

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">Transport Mode</label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                    {types.map(type => (
                      <button
                        key={type.id}
                        type="button"
                        onClick={() => setTransportType(type.id)}
                        className={`relative overflow-hidden group p-4 rounded-xl border flex flex-col items-center gap-3 transition-all duration-300 ${
                          transportType === type.id
                            ? 'border-primary-500 bg-primary-500/10 shadow-[0_0_20px_rgba(16,185,129,0.15)] scale-[1.02]'
                            : 'border-white/10 bg-black/20 hover:border-white/20 hover:bg-white/5'
                        }`}
                      >
                        {transportType === type.id && (
                          <div className="absolute inset-0 bg-gradient-to-b from-primary-500/10 to-transparent opacity-50"></div>
                        )}
                        <div className={`p-3 rounded-full bg-gradient-to-br ${type.color} text-white shadow-lg`}>
                          {type.icon}
                        </div>
                        <div className="text-center">
                          <div className="font-semibold">{type.name}</div>
                          <div className={`text-xs mt-1 ${type.id === 'car' ? 'text-red-400' : 'text-primary-400'}`}>{type.rate}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Distance (km)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    value={distance}
                    onChange={(e) => setDistance(e.target.value)}
                    placeholder="e.g. 5.5"
                    className="glass-input w-full"
                  />
                </div>

                <button type="submit" disabled={loading} className="btn-primary w-full py-3 text-lg">
                  {loading ? 'Logging...' : 'Log Activity'}
                </button>
              </div>
            </form>

            <div className="glass-card p-6">
              <h3 className="text-xl font-semibold mb-4">Recent Activity</h3>
              {history.length > 0 ? (
                <div className="space-y-3">
                  {history.map((entry, i) => (
                    <div key={i} className="p-4 bg-black/20 rounded-lg border border-white/5 flex items-center justify-between">
                      <div>
                        <div className="font-semibold capitalize">{entry.type}</div>
                        <div className="text-sm text-gray-400">{entry.distance_km} km</div>
                      </div>
                      <div className="text-xl font-bold text-primary-400">+{entry.eco_points_earned}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">No activity logged yet. Start with the form above!</div>
              )}
            </div>
          </div>

          <div className="glass-card p-6 h-fit">
            <h3 className="text-lg font-semibold mb-4">How It Works</h3>
            <div className="space-y-4 text-sm text-gray-400">
              <div>
                <div className="font-semibold text-white mb-1">🚶 Walking & Cycling</div>
                <p>Earn maximum points for sustainable transport!</p>
              </div>
              <div>
                <div className="font-semibold text-white mb-1">🚌 Public Transport</div>
                <p>Good choice! Earn solid eco points.</p>
              </div>
              <div>
                <div className="font-semibold text-white mb-1">🚗 Personal Vehicle</div>
                <p>We still track it, but try sustainable options instead!</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
