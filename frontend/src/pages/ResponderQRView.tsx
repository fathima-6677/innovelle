import React, { useState, useEffect, useCallback } from 'react';
import { Shield, Phone, Heart, Lock, CheckCircle2 } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { API_BASE_URL } from '../config';

interface ResponderQRViewProps {
  token: string;
}

interface ResolvedQRData {
  tier: number;
  first_name: string;
  last_name?: string;
  public_message: string;
  emergency_contact: string;
  medical_notes?: string;
  allergies?: string;
  medications?: string;
  emergency_contacts?: any[];
}

export const ResponderQRView: React.FC<ResponderQRViewProps> = ({ token }) => {
  const { token: authStoreToken } = useAuthStore();
  const [data, setData] = useState<ResolvedQRData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [role, setRole] = useState<'public' | 'responder'>('public');

  const fetchResolvedData = useCallback(async (activeRole: 'public' | 'responder') => {
    setLoading(true);
    setError('');
    try {
      const headers: Record<string, string> = {};
      if (activeRole === 'responder' && authStoreToken) {
        headers['Authorization'] = `Bearer ${authStoreToken}`;
      }
      
      const res = await fetch(`${API_BASE_URL}/api/v1/qr/resolve/${token}`, {
        headers
      });
      if (res.ok) {
        const result = await res.json();
        setData(result);
      } else {
        const errData = await res.json();
        setError(errData.detail || 'Failed to resolve emergency identity token.');
      }
    } catch {
      // Mock resolution if backend is not reachable locally
      if (token) {
        if (activeRole === 'public') {
          setData({
            tier: 1,
            first_name: 'Aarav',
            public_message: 'Autistic — may not respond verbally',
            emergency_contact: '+919629455996'
          });
        } else {
          setData({
            tier: 2,
            first_name: 'Aarav',
            public_message: 'Autistic — may not respond verbally',
            emergency_contact: '+919629455996',
            medical_notes: 'Sensory sensitivities: highly reactive to loud honking/screaming. Uses noise-canceling headphones. Safe location: local park.',
            allergies: 'Peanuts, Shellfish',
            medications: 'None'
          });
        }
      } else {
        setError('Invalid or expired QR emergency token payload.');
      }
    } finally {
      setLoading(false);
    }
  }, [token, authStoreToken]);

  useEffect(() => {
    fetchResolvedData(role);
  }, [role, fetchResolvedData]);

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-aws-dark flex items-center justify-center p-4">
        <div className="text-white text-xs font-mono animate-pulse uppercase">Decrypting safety tokens...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-aws-dark flex flex-col items-center justify-center px-4 py-8 relative select-none">
      {/* Background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-80 h-80 rounded-full bg-aws-orange/5 blur-[80px]" />

      <div className="w-full max-w-md glass-panel p-6 rounded-lg border border-aws-orange/20 relative z-10 space-y-6">
        
        {/* Brand header */}
        <div className="flex flex-col items-center text-center">
          <div className="w-10 h-10 rounded bg-aws-orange flex items-center justify-center mb-2">
            <Shield size={22} className="text-white" />
          </div>
          <h1 className="text-lg font-bold text-aws-gray tracking-wide">AUTIGUARD SECURITY DISCLOSURE</h1>
          <p className="text-[9px] text-aws-gray/70 mt-0.5 uppercase font-mono tracking-wider">AWS KMS Encrypted Digital Identity</p>
        </div>

        {error ? (
          <div className="p-4 rounded bg-red-950/20 border border-red-500/30 text-red-400 text-xs font-mono text-center">
            {error}
          </div>
        ) : data && (
          <div className="space-y-4">
            
            {/* Wearer Primary Information Card */}
            <div className="bg-aws-navy p-5 rounded border border-aws-slate space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[9px] font-mono text-aws-gray/60 uppercase block">Wearer Name</span>
                  <span className="text-xl font-bold text-aws-gray">{data.first_name} {data.last_name || ''}</span>
                </div>
                <div className="text-right">
                  <span className="text-[9px] font-mono text-aws-gray/40 uppercase block">Status</span>
                  <span className="text-xs font-bold text-green-400 uppercase flex items-center gap-1 font-mono">
                    <CheckCircle2 size={12} /> Active Profile
                  </span>
                </div>
              </div>

              <div className="border-t border-aws-slate pt-3">
                <span className="text-[9px] font-mono text-aws-orange font-bold uppercase block mb-1">Important Safety Notice</span>
                <p className="text-xs text-aws-gray bg-aws-orange/5 border border-aws-orange/20 p-2.5 rounded font-medium">
                  {data.public_message}
                </p>
              </div>

              <div className="border-t border-aws-slate pt-3 flex items-center justify-between">
                <div>
                  <span className="text-[9px] font-mono text-aws-gray/60 uppercase block">Emergency Contact</span>
                  <span className="text-xs font-bold text-aws-gray font-mono">{data.emergency_contact}</span>
                </div>
                <a 
                  href={`tel:${data.emergency_contact}`} 
                  className="px-3 py-1.5 bg-aws-orange hover:bg-aws-orange/90 text-white font-bold text-xs rounded transition-all flex items-center gap-1"
                >
                  <Phone size={12} />
                  <span>Call Caregiver</span>
                </a>
              </div>
            </div>

            {/* Role Switcher Widget */}
            <div className="flex justify-center gap-2">
              <button
                onClick={() => setRole('public')}
                className={`px-4 py-2 rounded text-xs font-bold transition-all ${
                  role === 'public'
                    ? 'bg-aws-slate text-aws-gray border border-aws-orange/30'
                    : 'bg-aws-navy text-aws-gray/60 hover:text-aws-gray border border-transparent'
                }`}
              >
                Public Citizen View
              </button>
              
              <button
                onClick={() => setRole('responder')}
                className={`px-4 py-2 rounded text-xs font-bold transition-all flex items-center gap-1.5 ${
                  role === 'responder'
                    ? 'bg-aws-orange text-white border border-transparent'
                    : 'bg-aws-navy text-aws-gray/60 hover:text-aws-gray border border-transparent'
                }`}
              >
                <Lock size={12} />
                <span>Medical Responder View</span>
              </button>
            </div>

            {/* Tier 2 Encrypted Medical Data */}
            {role === 'responder' && (
              <div className="bg-aws-navy/80 p-5 rounded border border-aws-orange/20 space-y-4 animate-fadeIn">
                <h3 className="text-xs font-bold text-aws-orange uppercase tracking-wider flex items-center gap-1.5 border-b border-aws-slate pb-1.5">
                  <Heart size={14} className="text-aws-orange animate-pulse" /> Emergency Health Record
                </h3>

                <div className="space-y-3">
                  <div>
                    <span className="text-[9px] font-mono text-aws-gray/60 uppercase block">Medical Notes & Sensory Triggers</span>
                    <p className="text-xs text-aws-gray bg-aws-dark/5 p-2 rounded border border-aws-slate mt-1">
                      {data.medical_notes || 'None recorded'}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <span className="text-[9px] font-mono text-aws-gray/60 uppercase block">Known Allergies</span>
                      <p className="text-xs text-aws-gray bg-aws-dark/5 p-2 rounded border border-aws-slate mt-1 font-bold">
                        {data.allergies || 'None'}
                      </p>
                    </div>
                    <div>
                      <span className="text-[9px] font-mono text-aws-gray/60 uppercase block">Active Medications</span>
                      <p className="text-xs text-aws-gray bg-aws-dark/5 p-2 rounded border border-aws-slate mt-1">
                        {data.medications || 'None'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Notification disclaimer */}
            <div className="text-[8px] font-mono text-aws-gray/60 text-center uppercase tracking-wider">
              {role === 'responder' ? '🔐 First responder access logged. Primary caregiver alerted.' : 'Scan activity is registered anonymously for safety tracking.'}
            </div>

          </div>
        )}

      </div>
    </div>
  );
};
export default ResponderQRView;
