import { useEffect, useState } from 'react';
import { getCampaigns, getCampaignDashboard } from '../services/api';
import { Link } from 'react-router-dom';

export default function AdminDashboard() {
  const [campaigns, setCampaigns] = useState([]);
  const [selected, setSelected] = useState(null);
  const selectedId = selected?.id;

  useEffect(() => {
    async function load() {
      try {
        const c = await getCampaigns();
        setCampaigns(c || []);
        if ((c || []).length > 0) setSelected(c[0]);
      } catch {
        setCampaigns([]);
        setSelected(null);
      }
    }
    load();
  }, []);

  useEffect(() => {
    async function loadDashboard() {
      if (!selectedId) return;
      try {
        const d = await getCampaignDashboard(selectedId);
        // attach basic stats
        setSelected(prev => prev && prev.id === selectedId ? ({...prev, dashboard: d}) : prev);
      } catch {
        setSelected(prev => prev && prev.id === selectedId ? ({...prev, dashboard: null}) : prev);
      }
    }
    loadDashboard();
  }, [selectedId]);

  return (
    <div className="min-h-screen pt-24 px-4 md:px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Admin Dashboard</h1>
            <p className="text-sm text-gray-400">Manage campaigns, users, and verification queue.</p>
          </div>
          <div className="space-x-2">
            <Link to="/admin/campaigns" className="btn-primary">Manage Campaigns</Link>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          <div className="card p-4">
            <div className="text-sm text-gray-400">Pending Proofs</div>
            <div className="text-3xl font-bold">--</div>
          </div>
          <div className="card p-4">
            <div className="text-sm text-gray-400">Total Campaigns</div>
            <div className="text-3xl font-bold">{campaigns.length}</div>
          </div>
          <div className="card p-4">
            <div className="text-sm text-gray-400">Leaderboards Managed</div>
            <div className="text-3xl font-bold">--</div>
          </div>
          <div className="card p-4">
            <div className="text-sm text-gray-400">Verification Rate</div>
            <div className="text-3xl font-bold">--</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="card p-4 lg:col-span-2">
            <h3 className="font-semibold mb-2">Sustainability Analytics</h3>
            <p className="text-sm text-gray-400">High level carbon reduction and campaign performance.</p>
          </div>
          <div className="card p-4">
            <h3 className="font-semibold mb-2">Audit Logs</h3>
            <p className="text-sm text-gray-400">Recent verification and admin actions.</p>
          </div>
        </div>

        <div className="card p-4">
          <h3 className="font-semibold mb-2">Campaigns</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {campaigns.map(c => (
              <div key={c.id} className="p-3 border rounded-lg bg-black/10">
                <div className="font-bold">{c.name}</div>
                <div className="text-xs text-gray-400">{c.goal}</div>
                <div className="mt-2 text-sm text-gray-300">Participants: {c?.dashboard?.total_participants ?? '--'}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
