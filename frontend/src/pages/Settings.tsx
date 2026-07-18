import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { useAuthStore } from '../store/authStore';
import { Settings as SettingsIcon, Shield, Bell, Phone, Check } from 'lucide-react';
import { API_BASE_URL } from '../config';

const SETTINGS_KEY = 'autiguard_settings';

export const Settings: React.FC = () => {
  const { user, token } = useAuthStore();

  // Load from localStorage on first render
  const saved = JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}');

  const [escalationMinutes, setEscalationMinutes] = useState<number>(saved.escalationMinutes ?? 5);
  const [primaryPhone, setPrimaryPhone] = useState<string>(saved.primaryPhone ?? '+919629455996');
  const [secondaryPhone, setSecondaryPhone] = useState<string>(saved.secondaryPhone ?? '+919876543210');
  const [enableWhatsapp, setEnableWhatsapp] = useState<boolean>(saved.enableWhatsapp ?? true);
  const [enableMfa, setEnableMfa] = useState<boolean>(saved.enableMfa ?? false);
  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);

  // Sync to localStorage whenever values change
  useEffect(() => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify({
      escalationMinutes, primaryPhone, secondaryPhone, enableWhatsapp, enableMfa
    }));
  }, [escalationMinutes, primaryPhone, secondaryPhone, enableWhatsapp, enableMfa]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const payload = { escalationMinutes, primaryPhone, secondaryPhone, enableWhatsapp, enableMfa };

    // Persist to localStorage immediately
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(payload));

    try {
      // Try to save to backend API
      await fetch(`${API_BASE_URL}/api/v1/auth/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload)
      });
      setMessage('Settings saved successfully and persisted to your account.');
    } catch {
      // Backend not available — localStorage save is enough for local use
      setMessage('Settings saved locally. Connect backend to sync across devices.');
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(''), 4000);
    }
  };


  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Navbar />

      <main className="flex-1 overflow-y-auto p-6 bg-aws-dark select-none">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
          <div>
            <h1 className="text-xl font-bold text-black flex items-center gap-2">
              <SettingsIcon className="text-aws-orange" size={24} />
              SYSTEM PREFERENCES & SETTINGS
            </h1>
            <p className="text-xs text-black/70 mt-1 uppercase font-mono">Notification dispatch rules & console variables</p>
          </div>
        </div>

        {message && (
          <div className="mb-6 p-4 rounded bg-aws-teal/10 border border-aws-teal/30 text-aws-teal text-xs font-mono text-center">
            {message}
          </div>
        )}

        <form onSubmit={handleSave} className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Notification settings */}
          <div className="lg:col-span-8 space-y-6">
            <div className="glass-panel p-6 rounded-lg border border-aws-slate space-y-4">
              <h2 className="text-xs font-bold text-black uppercase tracking-wider border-b border-aws-slate pb-2 flex items-center gap-1.5">
                <Bell size={16} className="text-aws-orange" /> Alert Dispatch Configuration
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-mono text-black/70 uppercase mb-1.5">Escalation Timer (Minutes)</label>
                  <input
                    type="number"
                    value={escalationMinutes}
                    onChange={(e) => setEscalationMinutes(parseInt(e.target.value))}
                    className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-xs text-black focus:outline-none focus:border-aws-orange font-mono"
                    min={1}
                    max={60}
                    required
                  />
                  <span className="text-[9px] text-black/50 mt-1 block">Time elapsed before cascading alerts to backup contacts</span>
                </div>

                <div className="flex items-center">
                  <label className="flex items-center gap-2 text-xs text-black cursor-pointer mt-4 select-none">
                    <input
                      type="checkbox"
                      checked={enableWhatsapp}
                      onChange={(e) => setEnableWhatsapp(e.target.checked)}
                      className="accent-aws-orange rounded w-4 h-4 bg-aws-navy border-aws-slate"
                    />
                    <span>Route warnings via Twilio WhatsApp Template API</span>
                  </label>
                </div>
              </div>
            </div>

            <div className="glass-panel p-6 rounded-lg border border-aws-slate space-y-4">
              <h2 className="text-xs font-bold text-black uppercase tracking-wider border-b border-aws-slate pb-2 flex items-center gap-1.5">
                <Phone size={16} className="text-aws-orange" /> Crisis Escalation Contacts
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-mono text-black/70 uppercase mb-1.5">Primary Caregiver Phone (India format)</label>
                  <input
                    type="text"
                    value={primaryPhone}
                    onChange={(e) => setPrimaryPhone(e.target.value)}
                    className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-xs text-black focus:outline-none focus:border-aws-orange font-mono"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-mono text-black/70 uppercase mb-1.5">Secondary Backup Phone</label>
                  <input
                    type="text"
                    value={secondaryPhone}
                    onChange={(e) => setSecondaryPhone(e.target.value)}
                    className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-xs text-black focus:outline-none focus:border-aws-orange font-mono"
                    required
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Security console */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="glass-panel p-6 rounded-lg border border-aws-slate space-y-4">
              <h2 className="text-xs font-bold text-black uppercase tracking-wider border-b border-aws-slate pb-2 flex items-center gap-1.5">
                <Shield size={16} className="text-aws-orange" /> AWS Portal Security
              </h2>

              <div className="space-y-4">
                <label className="flex items-start gap-2 text-xs text-black cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={enableMfa}
                    onChange={(e) => setEnableMfa(e.target.checked)}
                    className="accent-aws-orange rounded w-4 h-4 mt-0.5 bg-aws-navy border-aws-slate"
                  />
                  <div>
                    <span className="block font-bold">Enforce Session MFA</span>
                    <span className="block text-[9px] text-black/60 font-mono mt-0.5">Require TOTP token validation upon console entry</span>
                  </div>
                </label>

                <div className="pt-2 border-t border-aws-slate">
                  <span className="text-[10px] font-mono text-aws-teal uppercase font-bold block mb-1">User Identity Scope:</span>
                  <span className="text-[9px] text-black/60 font-mono block">Role: {user?.role || 'caregiver'}</span>
                  <span className="text-[9px] text-black/60 font-mono block">Pool: {user?.orgId || 'demo-org-99'}</span>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={saving}
              className="w-full py-3 bg-aws-orange hover:bg-aws-orange/90 disabled:opacity-60 text-black font-bold text-xs rounded flex items-center justify-center gap-1.5 transition-all"
            >
              <Check size={16} />
              <span>{saving ? 'Saving...' : 'Save System Settings'}</span>
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};
export default Settings;
