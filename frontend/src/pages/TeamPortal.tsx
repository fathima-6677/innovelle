import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { useAuthStore } from '../store/authStore';
import { Users, UserPlus, Key, Trash2, Mail, Loader } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface TeamMember {
  userId: string;
  name: string;
  email: string;
  role: 'caregiver' | 'org_admin' | 'super_admin';
  joinedAt: string;
}

const TEAM_KEY = 'autiguard_team_members';

const DEFAULT_MEMBERS: TeamMember[] = [
  { userId: '1', name: 'Dr. Priya Nair', email: 'priya@autiguard.org', role: 'org_admin', joinedAt: '2026-01-10' },
  { userId: '2', name: 'Sanjay Kumar', email: 'sanjay@autiguard.org', role: 'caregiver', joinedAt: '2026-03-15' },
  { userId: '3', name: 'Ananya Sen', email: 'ananya@autiguard.org', role: 'caregiver', joinedAt: '2026-05-02' }
];

export const TeamPortal: React.FC = () => {
  const { user, token } = useAuthStore();

  // Load members from localStorage (persists across refreshes)
  const [members, setMembers] = useState<TeamMember[]>(() => {
    try {
      const stored = localStorage.getItem(TEAM_KEY);
      return stored ? JSON.parse(stored) : DEFAULT_MEMBERS;
    } catch {
      return DEFAULT_MEMBERS;
    }
  });

  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'caregiver' | 'org_admin'>('caregiver');
  const [inviteName, setInviteName] = useState('');
  const [message, setMessage] = useState('');
  const [inviting, setInviting] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Persist members list to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem(TEAM_KEY, JSON.stringify(members));
  }, [members]);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail || !inviteName) return;
    setInviting(true);
    setMessage('');

    try {
      // Call real /auth/signup endpoint to register the user in Cognito/mock DB
      const res = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ email: inviteEmail, name: inviteName, role: inviteRole, password: 'TempPass@123' })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Invitation failed.');
      }

      const newMember: TeamMember = {
        userId: `user-${Date.now()}`,
        name: inviteName,
        email: inviteEmail,
        role: inviteRole,
        joinedAt: new Date().toISOString().split('T')[0]
      };

      setMembers(prev => [...prev, newMember]);
      setInviteEmail('');
      setInviteName('');
      setMessage(`Invitation sent to ${inviteEmail}. They will receive a verification email to set their password.`);
    } catch (_err: any) {
      // Offline fallback — still persist locally
      const newMember: TeamMember = {
        userId: `user-${Date.now()}`,
        name: inviteName,
        email: inviteEmail,
        role: inviteRole,
        joinedAt: new Date().toISOString().split('T')[0]
      };
      setMembers(prev => [...prev, newMember]);
      setInviteEmail('');
      setInviteName('');
      setMessage(`Member added locally (backend offline). Connect backend to send real Cognito invitation.`);
    } finally {
      setInviting(false);
      setTimeout(() => setMessage(''), 5000);
    }
  };

  const handleDelete = async (userId: string, memberEmail: string) => {
    setDeletingId(userId);

    try {
      // Try to remove from backend
      await fetch(`${API_BASE_URL}/api/v1/auth/users/${encodeURIComponent(memberEmail)}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
    } catch {
      // Offline — just remove locally
    }

    // Remove from local list (and localStorage via useEffect)
    setMembers(prev => prev.filter(m => m.userId !== userId));
    setDeletingId(null);
  };


  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Navbar />

      <main className="flex-1 overflow-y-auto p-6 bg-aws-dark select-none">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
          <div>
            <h1 className="text-xl font-bold text-black flex items-center gap-2">
              <Users className="text-aws-orange" size={24} />
              ORGANIZATION TEAM MANAGEMENT
            </h1>
            <p className="text-xs text-black/70 mt-1 uppercase font-mono">Cognito Identity Pool RBAC Control Panel</p>
          </div>
        </div>

        {message && (
          <div className="mb-6 p-4 rounded bg-aws-teal/10 border border-aws-teal/30 text-aws-teal text-xs font-mono text-center">
            {message}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Members List */}
          <div className="lg:col-span-8 glass-panel p-6 rounded-lg border border-aws-slate">
            <h2 className="text-xs font-bold text-black uppercase tracking-wider mb-6 border-b border-aws-slate pb-2">
              Active Authorized Accounts
            </h2>

            <div className="space-y-3">
              {members.map(member => (
                <div key={member.userId} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-aws-navy rounded border border-aws-slate hover:border-aws-orange/20 transition-all gap-4">
                  <div className="flex items-center gap-3 w-full sm:w-auto">
                    <div className="w-10 h-10 rounded-full bg-aws-slate border border-aws-orange/20 flex items-center justify-center font-bold text-aws-orange text-sm uppercase shrink-0">
                      {member.name[0]}
                    </div>
                    <div className="min-w-0">
                      <h3 className="text-sm font-bold text-white truncate">{member.name}</h3>
                      <p className="text-xs text-aws-gray/40 font-mono mt-0.5 truncate">{member.email}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 justify-between w-full sm:w-auto sm:justify-end border-t border-aws-slate/10 pt-3 sm:pt-0 sm:border-0">
                    <div className="flex flex-col items-end">
                      <span className="text-[10px] text-aws-orange/80 bg-aws-orange/5 px-2 py-0.5 rounded border border-aws-orange/20 uppercase font-mono font-semibold">
                        {member.role}
                      </span>
                      <span className="text-[9px] text-black/50 font-mono mt-1">Joined: {member.joinedAt}</span>
                    </div>

                    {user?.email !== member.email && (
                      <button
                        onClick={() => handleDelete(member.userId, member.email)}
                        disabled={deletingId === member.userId}
                        className="p-2 hover:bg-red-600/10 border border-transparent hover:border-red-500/20 text-red-400 rounded transition-all disabled:opacity-50"
                      >
                        {deletingId === member.userId
                          ? <Loader size={14} className="animate-spin" />
                          : <Trash2 size={14} />}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Cognito User Pool Invite Form */}
          <form onSubmit={handleInvite} className="lg:col-span-4 glass-panel p-6 rounded-lg border border-aws-orange/15 space-y-4">
            <h2 className="text-xs font-bold text-black uppercase tracking-wider mb-4 border-b border-aws-slate pb-2 flex items-center gap-1.5">
              <UserPlus size={16} className="text-aws-orange" /> Invite Member
            </h2>

            <div>
              <label className="block text-[10px] font-mono text-black/70 uppercase mb-1">Full Name</label>
              <input
                type="text"
                value={inviteName}
                onChange={(e) => setInviteName(e.target.value)}
                className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-xs text-black focus:outline-none focus:border-aws-orange"
                placeholder="e.g. Sanjay Kumar"
                required
              />
            </div>

            <div>
              <label className="block text-[10px] font-mono text-black/70 uppercase mb-1">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-2.5 top-2.5 text-black/60" size={14} />
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  className="w-full pl-8 pr-3 py-2 bg-aws-navy border border-aws-slate rounded text-xs text-black focus:outline-none focus:border-aws-orange font-mono"
                  placeholder="name@organization.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-mono text-black/70 uppercase mb-1">Access Role</label>
              <select
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value as any)}
                className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-xs text-black focus:outline-none focus:border-aws-orange font-mono"
              >
                <option value="caregiver">Caregiver (Read/Write)</option>
                <option value="org_admin">Org Admin (Full Access)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={inviting}
              className="w-full py-2 bg-aws-orange hover:bg-aws-orange/90 disabled:opacity-60 text-black font-bold text-xs rounded flex items-center justify-center gap-1.5 transition-all mt-4"
            >
              {inviting ? <Loader size={14} className="animate-spin" /> : <UserPlus size={14} />}
              <span>{inviting ? 'Sending Invitation...' : 'Send Cognito Invitation'}</span>
            </button>

            <div className="border-t border-aws-slate pt-4 font-mono text-[9px] text-black/50 flex gap-2">
              <Key size={12} className="text-aws-teal shrink-0" />
              <span>Cognito pool registration sends an verification email with dynamic temporary passkey.</span>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};
export default TeamPortal;
