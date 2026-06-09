const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function uploadProof(userId, proofType, file) {
  const form = new FormData();
  form.append('file', file);
  const url = `${API_BASE}/users/${userId}/proofs/?proof_type=${encodeURIComponent(proofType)}`;
  const resp = await fetch(url, {
    method: 'POST',
    body: form,
  });
  return resp.json();
}

export async function getDashboard(userId) {
  const url = `${API_BASE}/users/${userId}/dashboard/`;
  const resp = await fetch(url);
  return resp.json();
}

export async function getWalkingStats() {
  const url = `${API_BASE}/walking/stats`;
  const resp = await fetch(url, { credentials: 'include' });
  return resp.json();
}

export async function submitWalking(payload, file=null) {
  const form = new FormData();
  form.append('steps', payload.steps);
  if (payload.distance_km) form.append('distance_km', payload.distance_km);
  form.append('purpose', payload.purpose || 'Other');
  if (file) form.append('file', file);
  const resp = await fetch(`${API_BASE}/walking/submit`, { method: 'POST', body: form, credentials: 'include' });
  return resp.json();
}

export async function getCampaignDashboard(campaignId) {
  const url = `${API_BASE}/campaigns/${campaignId}/dashboard/`;
  const resp = await fetch(url);
  return resp.json();
}

export async function getCampaigns() {
  const url = `${API_BASE}/admin/campaigns/`;
  const resp = await fetch(url);
  return resp.json();
}

export async function getCampaignLeaderboard(campaignId) {
  const url = `${API_BASE}/campaigns/${campaignId}/leaderboard/`;
  const resp = await fetch(url);
  return resp.json();
}
