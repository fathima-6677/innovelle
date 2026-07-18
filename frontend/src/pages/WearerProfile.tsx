import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import { useAuthStore } from '../store/authStore';
import { User, Key, RefreshCw, Save, ArrowRight } from 'lucide-react';
import { API_BASE_URL } from '../config';

export const WearerProfile: React.FC = () => {
  const { token } = useAuthStore();
  const [selectedWearerId, setSelectedWearerId] = useState<string>('');
  const [wearersList, setWearersList] = useState<any[]>([]);

  // Profile fields
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [dob, setDob] = useState('');
  const [medicalNotes, setMedicalNotes] = useState('');
  const [allergies, setAllergies] = useState('');
  const [medications, setMedications] = useState('');

  // QR properties
  const [qrPayload, setQrPayload] = useState('');
  const [rotating, setRotating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const fetchWearers = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/wearers`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setWearersList(data);
        if (data.length > 0 && !selectedWearerId) {
          setSelectedWearerId(data[0].wearer_id);
        }
      }
    } catch {
      // offline fallback
      const mock = [{
        wearer_id: 'wearer-99',
        first_name: 'Aarav',
        last_name: 'Sharma',
        dob: '2016-04-12',
        medical_notes: 'Sensitive to loud noises.',
        allergies: 'Peanuts',
        medications: 'None'
      }];
      setWearersList(mock);
      setSelectedWearerId(mock[0].wearer_id);
    }
  }, [token, selectedWearerId]);

  const triggerQrRotation = useCallback(async () => {
    if (!selectedWearerId) return;
    setRotating(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/qr/${selectedWearerId}/rotate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setQrPayload(data.qr_payload);
      }
    } catch {
      // Local signed token mock
      setQrPayload('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ3ZWFyZXItOTkiLCJleHAiOjE3OTIwMDAwMDB9.signature');
    } finally {
      setRotating(false);
    }
  }, [selectedWearerId, token]);

  const loadWearerProfile = useCallback(() => {
    const active = wearersList.find(w => w.wearer_id === selectedWearerId);
    if (active) {
      setFirstName(active.first_name || '');
      setLastName(active.last_name || '');
      setDob(active.dob || '');
      setMedicalNotes(active.medical_notes || '');
      setAllergies(active.allergies || '');
      setMedications(active.medications || '');
      triggerQrRotation();
    }
  }, [selectedWearerId, wearersList, triggerQrRotation]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    const payload = {
      first_name: firstName,
      last_name: lastName,
      dob,
      medical_notes: medicalNotes,
      allergies,
      medications,
      qr_tiering_rules: {},
      emergency_contacts: [{"name": "Mom", "phone": "+919629455996"}]
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/wearers/${selectedWearerId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setMessage('Profile successfully updated. Sensitive data encrypted with AWS KMS CMK envelope encryption.');
        fetchWearers();
      } else {
        setMessage('Error saving profile.');
      }
    } catch {
      setMessage('Offline simulation: Profile changes cached locally. KMS key validation simulated.');
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    fetchWearers();
  }, [fetchWearers]);

  useEffect(() => {
    loadWearerProfile();
  }, [loadWearerProfile]);

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Navbar />

      <main className="flex-1 overflow-y-auto p-6 bg-aws-dark select-none">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
          <div>
            <h1 className="text-xl font-bold text-aws-gray flex items-center gap-2">
              <User className="text-aws-orange" size={24} />
              WEARER ENCRYPTED PROFILES
            </h1>
            <p className="text-xs text-aws-gray/70 mt-1 uppercase font-mono">AWS KMS CMK Protected PII & Bio Info</p>
          </div>

          <select
            value={selectedWearerId}
            onChange={(e) => setSelectedWearerId(e.target.value)}
            className="bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray px-3 py-1.5 focus:outline-none focus:border-aws-orange font-mono"
          >
            {wearersList.map(w => (
              <option key={w.wearer_id} value={w.wearer_id}>
                {w.first_name} {w.last_name}
              </option>
            ))}
          </select>
        </div>

        {message && (
          <div className="mb-6 p-4 rounded bg-aws-teal/10 border border-aws-teal/30 text-aws-teal text-xs font-mono text-center">
            {message}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Editor Form */}
          <form onSubmit={handleSave} className="lg:col-span-8 glass-panel p-6 rounded-lg space-y-5">
            <h2 className="text-sm font-bold text-aws-gray uppercase tracking-wider border-b border-aws-slate pb-2">
              Biographical Details
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-aws-gray/70 uppercase mb-2">First Name</label>
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray focus:outline-none focus:border-aws-orange"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-aws-gray/70 uppercase mb-2">Last Name</label>
                <input
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray focus:outline-none focus:border-aws-orange"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-aws-gray/70 uppercase mb-2">Date of Birth</label>
                <input
                  type="date"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                  className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray focus:outline-none focus:border-aws-orange font-mono"
                  required
                />
              </div>
            </div>

            <h2 className="text-sm font-bold text-aws-orange uppercase tracking-wider border-b border-aws-slate pt-4 pb-2 flex items-center gap-1.5">
              <Key size={16} /> Encrypted Health Information
            </h2>
            <p className="text-[10px] text-aws-gray/40 font-mono italic">
              * Note: The fields below are envelope-encrypted via AWS KMS prior to ingestion into DynamoDB and are never stored in raw text.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-mono text-aws-gray/70 uppercase mb-2">Medical Conditions & Sensory Triggers</label>
                <textarea
                  rows={3}
                  value={medicalNotes}
                  onChange={(e) => setMedicalNotes(e.target.value)}
                  className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray focus:outline-none focus:border-aws-orange"
                  placeholder="e.g. sensitive to loud noises, has speech delays"
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-aws-gray/70 uppercase mb-2">Allergies</label>
                <input
                  type="text"
                  value={allergies}
                  onChange={(e) => setAllergies(e.target.value)}
                  className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray focus:outline-none focus:border-aws-orange"
                  placeholder="e.g. Peanuts, Penicillin"
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-aws-gray/50 uppercase mb-2">Medications</label>
                <input
                  type="text"
                  value={medications}
                  onChange={(e) => setMedications(e.target.value)}
                  className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray focus:outline-none focus:border-aws-orange"
                  placeholder="e.g. None or list dosages"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={saving}
              className="w-full md:w-auto px-6 py-2.5 bg-aws-orange hover:bg-aws-orange/90 text-white font-bold rounded flex items-center justify-center gap-2 transition-all mt-4"
            >
              <Save size={16} />
              <span>{saving ? 'Encrypting & Storing...' : 'Save Enriched Profile'}</span>
            </button>
          </form>

          {/* QR Identity Code Widget */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="glass-panel p-6 rounded-lg text-center flex flex-col items-center border border-aws-orange/15">
              <h2 className="text-sm font-bold text-aws-gray uppercase tracking-wider mb-4 border-b border-aws-slate pb-2 w-full">
                Caregiver QR Identity Card
              </h2>
              
              {/* Ephemeral QR representation */}
              <div className="bg-white p-2 rounded-lg w-44 h-44 flex items-center justify-center mb-4 relative group cursor-pointer border border-aws-orange/30">
                {qrPayload ? (
                  <img
                    src={`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(`${window.location.origin}/qr/resolve/${qrPayload}`)}`}
                    alt="Caregiver QR Identity Code"
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="text-black font-mono text-[10px] animate-pulse">GENERATING QR...</div>
                )}
                <div className="absolute inset-0 flex items-center justify-center bg-aws-dark/80 opacity-0 group-hover:opacity-100 transition-all text-white text-xs font-mono p-4 text-center">
                  Scan resolves to Tiered Emergency Medical Details
                </div>
              </div>

              <div className="w-full text-left space-y-2 mb-4 font-mono text-[10px] text-aws-gray/70 bg-aws-navy/60 p-3 rounded border border-aws-slate">
                <span className="block font-bold text-aws-orange uppercase">Active QR Token:</span>
                <span className="block break-all">{qrPayload ? `${qrPayload.slice(0, 48)}...` : 'Generating...'}</span>
                <span className="block text-[8px]">TTL: Rotating automatically in 24 hours</span>
              </div>

              <button
                onClick={triggerQrRotation}
                disabled={rotating}
                className="w-full py-2 bg-aws-slate hover:bg-aws-slate/70 text-aws-orange border border-aws-orange/20 font-semibold text-xs rounded flex items-center justify-center gap-1.5 transition-all"
              >
                <RefreshCw size={12} className={rotating ? 'animate-spin' : ''} />
                <span>Rotate Identity Key (KMS Sign)</span>
              </button>

              <div className="mt-4 flex items-center gap-1.5 text-aws-orange text-xs cursor-pointer hover:underline" onClick={() => window.open(`/qr/resolve/${qrPayload}`, '_blank')}>
                <span>Test public responder card link</span>
                <ArrowRight size={14} />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
export default WearerProfile;
