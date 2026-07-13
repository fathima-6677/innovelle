import React, { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { Shield, Eye, EyeOff, Lock, Mail, ArrowRight } from 'lucide-react';
import { API_BASE_URL } from '../config';

export const Login: React.FC = () => {
  const { login } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const [step, setStep] = useState<'credentials' | 'mfa'>('credentials');
  const [mfaCode, setMfaCode] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Call mock auth endpoint
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        throw new Error('Authentication failed. Incorrect email or password.');
      }

      const data = await response.json();
      
      // Simulating MFA Trigger for demo
      if (email.includes('mfa')) {
        setStep('mfa');
        setLoading(false);
        return;
      }

      login(data.access_token, {
        email,
        name: data.name || 'Demo Caregiver',
        role: data.role || 'caregiver',
        orgId: data.org_id || 'ORG#demo-org-99'
      });
    } catch (err: any) {
      // Offline fallback for demo if backend isn't launched yet
      if (email === 'admin@autiguard.org' || email === 'caregiver@autiguard.org') {
        login('mock-jwt-token', {
          email,
          name: email.startsWith('admin') ? 'Administrator' : 'Primary Caregiver',
          role: email.startsWith('admin') ? 'org_admin' : 'caregiver',
          orgId: 'ORG#demo-org-99'
        });
      } else {
        setError(err.message || 'Server connection timed out.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleMfaSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (mfaCode === '123456' || mfaCode.length === 6) {
      login('mock-jwt-token-mfa', {
        email,
        name: 'MFA Verified Caregiver',
        role: 'caregiver',
        orgId: 'ORG#demo-org-99'
      });
    } else {
      setError('Invalid verification code.');
    }
  };

  return (
    <div className="min-h-screen bg-aws-dark flex items-center justify-center px-4 relative select-none">
      {/* Premium background glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-aws-orange/15 blur-[120px]" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-aws-teal/15 blur-[120px]" />

      <div className="w-full max-w-md glass-panel p-8 rounded-lg glow-orange border border-aws-orange/10 relative z-10">
        {/* Brand */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded bg-aws-orange flex items-center justify-center mb-3">
            <Shield size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-aws-gray tracking-wide">AUTIGUARD</h1>
          <p className="text-xs text-aws-gray/70 mt-1 uppercase font-mono tracking-widest">Caregiver Control Center</p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded bg-red-900/20 border border-red-500/30 text-red-600 text-xs font-mono text-center">
            {error}
          </div>
        )}

        {step === 'credentials' ? (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-mono text-aws-gray/70 uppercase mb-2">AWS Portal Identity (Email)</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3.5 text-aws-gray/40" size={16} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray focus:outline-none focus:border-aws-orange transition-all font-mono"
                  placeholder="name@organization.com"
                  required
                />
              </div>
              <span className="text-[10px] text-aws-gray/60 mt-1 block">Try <b>admin@autiguard.org</b> or <b>caregiver@autiguard.org</b></span>
            </div>

            <div>
              <label className="block text-xs font-mono text-aws-gray/70 uppercase mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-3.5 text-aws-gray/40" size={16} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-3 bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray focus:outline-none focus:border-aws-orange transition-all font-mono"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3.5 text-aws-gray/40 hover:text-aws-gray"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 bg-aws-orange hover:bg-aws-orange/90 text-white font-bold rounded transition-all mt-6"
            >
              <span>{loading ? 'Verifying Session...' : 'Sign In To Console'}</span>
              <ArrowRight size={16} />
            </button>
          </form>
        ) : (
          <form onSubmit={handleMfaSubmit} className="space-y-5">
            <div className="text-center mb-4">
              <p className="text-sm text-aws-gray/70">MFA verification required. Enter the 6-digit code sent to your authenticator or SMS.</p>
            </div>
            <div>
              <label className="block text-xs font-mono text-aws-gray/70 uppercase mb-2">MFA Code</label>
              <input
                type="text"
                maxLength={6}
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value)}
                className="w-full text-center py-3 bg-aws-navy border border-aws-slate rounded text-lg font-bold text-aws-gray tracking-widest focus:outline-none focus:border-aws-orange transition-all font-mono"
                placeholder="000000"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full py-3 bg-aws-orange hover:bg-aws-orange/90 text-white font-bold rounded transition-all mt-4"
            >
              Verify OTP Code
            </button>
            <button
              type="button"
              onClick={() => setStep('credentials')}
              className="w-full text-center text-xs text-aws-orange hover:underline font-mono"
            >
              Back to Sign In
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
export default Login;
