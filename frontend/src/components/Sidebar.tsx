import React from 'react';
import { LayoutDashboard, Users, User, Map, MessageSquare, LineChart, Settings, LogOut } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

interface SidebarProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, setCurrentPage }) => {
  const { logout, user } = useAuthStore();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['caregiver', 'org_admin', 'super_admin'] },
    { id: 'profile', label: 'Wearers', icon: User, roles: ['caregiver', 'org_admin', 'super_admin'] },
    { id: 'geofence', label: 'Geofencing', icon: Map, roles: ['caregiver', 'org_admin', 'super_admin'] },
    { id: 'comms', label: 'Comm Assist Logs', icon: MessageSquare, roles: ['caregiver', 'org_admin', 'super_admin'] },
    { id: 'reports', label: 'Reports', icon: LineChart, roles: ['caregiver', 'org_admin', 'super_admin'] },
    { id: 'team', label: 'Team Portal', icon: Users, roles: ['org_admin', 'super_admin'] },
    { id: 'settings', label: 'Settings', icon: Settings, roles: ['caregiver', 'org_admin', 'super_admin'] },
  ];

  const visibleItems = menuItems.filter(item => item.roles.includes(user?.role || 'caregiver'));

  return (
    <div className="w-full md:w-64 bg-aws-navy border-b md:border-r border-aws-slate flex flex-col md:h-screen select-none flex-shrink-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between md:justify-start px-4 md:px-6 border-b border-aws-slate gap-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-aws-orange flex items-center justify-center font-bold text-white">
            AG
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-aws-gray tracking-wide">AUTIGUARD</span>
            <span className="text-xs text-aws-orange font-semibold tracking-widest uppercase hidden md:block">Console v1.0</span>
          </div>
        </div>
        <button onClick={logout} className="md:hidden text-aws-orange p-2 hover:bg-aws-slate/40 rounded transition-all">
          <LogOut size={20} />
        </button>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 px-2 md:px-4 py-2 md:py-6 flex flex-row md:flex-col overflow-x-auto md:overflow-y-auto space-x-2 md:space-x-0 md:space-y-1.5 scrollbar-hide">
        {visibleItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`flex-shrink-0 flex items-center gap-2 md:gap-3 px-3 md:px-4 py-2 md:py-3 rounded text-sm font-medium transition-all ${
                isActive
                  ? 'bg-aws-slate text-aws-orange border-b-2 md:border-b-0 md:border-l-2 border-aws-orange'
                  : 'text-aws-gray/70 hover:text-aws-gray hover:bg-aws-slate/40'
              }`}
            >
              <Icon size={18} className={isActive ? 'text-aws-orange' : 'text-aws-gray/50'} />
              <span className="whitespace-nowrap">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* User Status / Logout (Desktop Only) */}
      <div className="hidden md:block p-4 border-t border-aws-slate bg-aws-dark/50">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 rounded-full bg-aws-slate border border-aws-orange/20 flex items-center justify-center font-bold text-aws-orange text-sm uppercase">
            {user?.name?.[0] || 'C'}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-xs font-semibold text-aws-gray truncate">{user?.name}</span>
            <span className="text-[10px] text-aws-orange/80 uppercase font-mono tracking-wider">{user?.role}</span>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded bg-red-600/10 hover:bg-red-600/25 border border-red-500/20 text-red-400 text-xs font-medium transition-all"
        >
          <LogOut size={14} />
          <span>Sign Out Session</span>
        </button>
      </div>
    </div>
  );
};
