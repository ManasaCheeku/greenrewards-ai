import { useState } from 'react';
import { uploadProof } from '../services/api';
import { auth } from '../utils/auth';

export default function UploadProof() {
  const [file, setFile] = useState(null);
  const [proofType, setProofType] = useState('travel');
  const [status, setStatus] = useState(null);

  const user = auth.getCurrentUser();
  const userId = user?.id || 1;

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) return setStatus('Please choose a file');
    setStatus('Uploading...');
    try {
      const res = await uploadProof(userId, proofType, file);
      setStatus(`Uploaded. Proof ID: ${res.proof_id}`);
    } catch {
      setStatus('Upload failed');
    }
  }

  return (
    <div className="min-h-screen pt-24 px-4 md:px-8">
      <div className="max-w-3xl mx-auto glass-card p-6">
        <h2 className="text-2xl font-bold mb-4">Upload Proof</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Proof Type</label>
            <select value={proofType} onChange={(e) => setProofType(e.target.value)} className="input">
              <option value="travel">Travel</option>
              <option value="food">Sustainable Food</option>
              <option value="waste">Waste Management</option>
              <option value="energy">Energy Saving</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">File</label>
            <input type="file" accept="image/*,application/pdf" onChange={(e) => setFile(e.target.files[0])} />
          </div>

          <div>
            <button className="btn-primary" type="submit">Upload Proof</button>
          </div>

          {status && <div className="text-sm text-gray-300">{status}</div>}
        </form>
      </div>
    </div>
  );
}
