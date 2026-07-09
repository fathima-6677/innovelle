import React from 'react';
import { Bell, RefreshCw, Server, AlertTriangle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

interface NavbarProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onRefresh, isRefreshing }) => {
  const { user } = useAuthStore();

  return (
    <header className="h-16 bg-aws-navy border-b border-aws-slate px-6 flex items-center justify-between select-none">
      {/* Search / Org Identifier */}
      <div className="flex items-center gap-3">
        <Server size={18} className="text-aws-orange" />
        <span className="text-xs font-mono text-aws-gray/50 uppercase">Region:</span>
        <span className="text-xs font-mono text-aws-gray bg-aws-slate/60 px-2 py-0.5 rounded">ap-south-1 (Mumbai)</span>
        
        <span className="text-aws-slate">|</span>
        
        <span className="text-xs font-mono text-aws-gray/50 uppercase">Organization:</span>
        <span className="text-xs font-mono text-aws-orange font-bold uppercase">{user?.orgId || 'ORG#demo-org-99'}</span>
      </div>

      {/* Control Widgets */}
      <div className="flex items-center gap-4">
        {/* Refresh Indicator */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-2 hover:bg-aws-slate rounded text-aws-gray hover:text-aws-orange transition-all disabled:opacity-50"
            title="Refresh Live Metrics"
          >
            <RefreshCw size={16} className={isRefreshing ? 'animate-spin text-aws-orange' : ''} />
          </button>
        )}

        {/* Global Connection Status */}
        <div className="flex items-center gap-1.5 bg-green-500/10 border border-green-500/20 px-2 py-1 rounded">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-ping" />
          <span className="text-[10px] text-green-600 font-mono font-semibold uppercase">Cloud Link Active</span>
        </div>

        {/* Notification Alert Feed Indicator */}
        <div className="relative cursor-pointer p-2 hover:bg-aws-slate rounded text-aws-gray hover:text-aws-orange transition-all">
          <Bell size={18} />
          <div className="absolute top-1.5 right-1.5 w-2 h-2 bg-aws-orange rounded-full glow-orange" />
        </div>
      </div>
    </header>
  );
};
