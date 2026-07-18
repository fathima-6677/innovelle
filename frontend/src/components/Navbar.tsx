import React, { useState, useEffect } from 'react';
import { Bell, RefreshCw, Server, Menu, WifiOff } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { AWS_REGION, API_BASE_URL } from '../config';

interface NavbarProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onRefresh, isRefreshing }) => {
  const { user, setSidebarOpen } = useAuthStore();
  const [isOnline, setIsOnline] = useState<boolean | null>(null); // null = checking

  // ── Health ping every 30s ──────────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;

    const ping = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/`, { method: 'GET', signal: AbortSignal.timeout(4000) });
        if (!cancelled) setIsOnline(res.ok);
      } catch {
        if (!cancelled) setIsOnline(false);
      }
    };

    ping(); // immediate first check
    const timer = setInterval(ping, 30000); // re-check every 30s

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const statusConfig = isOnline === null
    ? { label: 'Checking', dotClass: 'bg-amber-400 animate-pulse', ringClass: 'bg-amber-400/10 border-amber-400/20', textClass: 'text-amber-500' }
    : isOnline
    ? { label: 'Active', dotClass: 'bg-green-500 animate-ping', ringClass: 'bg-green-500/10 border-green-500/20', textClass: 'text-green-600' }
    : { label: 'Offline', dotClass: 'bg-red-500', ringClass: 'bg-red-500/10 border-red-500/20', textClass: 'text-red-500' };

  return (
    <header className="h-16 bg-aws-navy border-b border-aws-slate px-4 md:px-6 flex items-center justify-between select-none">
      {/* Search / Org Identifier */}
      <div className="flex items-center gap-2 md:gap-3 min-w-0">
        {/* Hamburger Menu Icon for Mobile */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden p-2 hover:bg-aws-slate rounded text-aws-gray hover:text-aws-orange transition-all"
        >
          <Menu size={20} />
        </button>

        <Server size={18} className="text-aws-orange shrink-0 hidden sm:block" />
        <span className="text-[10px] md:text-xs font-mono text-aws-gray/50 uppercase hidden md:inline">Region:</span>
        <span className="text-[10px] md:text-xs font-mono text-aws-gray bg-aws-slate/60 px-2 py-0.5 rounded truncate">{AWS_REGION}</span>
        
        <span className="text-aws-slate hidden sm:inline">|</span>
        
        <span className="text-[10px] md:text-xs font-mono text-aws-gray/50 uppercase hidden md:inline">Org:</span>
        <span className="text-[10px] md:text-xs font-mono text-aws-orange font-bold uppercase truncate">{user?.orgId || 'demo-org-99'}</span>
      </div>

      {/* Control Widgets */}
      <div className="flex items-center gap-2 md:gap-4 shrink-0">
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

        {/* Global Connection Status — live health ping */}
        <div className={`flex items-center gap-1.5 border px-2 py-1 rounded ${statusConfig.ringClass}`}>
          {isOnline === false
            ? <WifiOff size={10} className={statusConfig.textClass} />
            : <div className={`w-1.5 h-1.5 rounded-full ${statusConfig.dotClass}`} />
          }
          <span className={`text-[9px] md:text-[10px] font-mono font-semibold uppercase hidden xs:inline ${statusConfig.textClass}`}>
            {statusConfig.label}
          </span>
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
