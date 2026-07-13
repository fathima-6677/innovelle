import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import { useAuthStore } from '../store/authStore';
import { MessageSquare, Calendar, Coffee, AlertTriangle, HelpCircle, Smile } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface CommLog {
  event_id: string;
  wearer_id: string;
  category_code: string;
  timestamp: string;
}

export const CommAssistLogs: React.FC = () => {
  const { token } = useAuthStore();
  const [selectedWearerId, setSelectedWearerId] = useState<string>('');
  const [wearersList, setWearersList] = useState<any[]>([]);
  const [logs, setLogs] = useState<CommLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterCode, setFilterCode] = useState<string>('ALL');

  useEffect(() => {
    const fetchWearers = async () => {
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
        const mock = [{ wearer_id: 'wearer-99', first_name: 'Aarav', last_name: 'Sharma' }];
        setWearersList(mock);
        setSelectedWearerId(mock[0].wearer_id);
      }
    };
    fetchWearers();
  }, [token, selectedWearerId]);

  const fetchLogs = useCallback(async () => {
    if (!selectedWearerId) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/comms/${selectedWearerId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setLogs(data);
      }
    } catch {
      // Offline fallback mock data
      setLogs([
        { event_id: '1', wearer_id: selectedWearerId, category_code: 'HUNGER', timestamp: new Date(Date.now() - 3600000 * 2).toISOString() },
        { event_id: '2', wearer_id: selectedWearerId, category_code: 'RESTROOM', timestamp: new Date(Date.now() - 3600000 * 5).toISOString() },
        { event_id: '3', wearer_id: selectedWearerId, category_code: 'ANXIETY', timestamp: new Date(Date.now() - 3600000 * 12).toISOString() },
        { event_id: '4', wearer_id: selectedWearerId, category_code: 'DISCOMFORT', timestamp: new Date(Date.now() - 3600000 * 24).toISOString() },
        { event_id: '5', wearer_id: selectedWearerId, category_code: 'HUNGER', timestamp: new Date(Date.now() - 3600000 * 28).toISOString() },
      ]);
    } finally {
      setLoading(false);
    }
  }, [selectedWearerId, token]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const getCategoryDetails = (code: string) => {
    switch (code.toUpperCase()) {
      case 'HUNGER':
        return { label: 'Hunger Assist', color: 'text-amber-500 bg-amber-500/10 border-amber-500/30', icon: Coffee };
      case 'RESTROOM':
        return { label: 'Restroom request', color: 'text-blue-500 bg-blue-500/10 border-blue-500/30', icon: Smile };
      case 'ANXIETY':
        return { label: 'Anxiety relief triggered', color: 'text-aws-orange bg-aws-orange/10 border-aws-orange/30', icon: AlertTriangle };
      case 'DISCOMFORT':
        return { label: 'Discomfort notification', color: 'text-red-500 bg-red-500/10 border-red-500/30', icon: HelpCircle };
      default:
        return { label: code, color: 'text-aws-teal bg-aws-teal/10 border-aws-teal/30', icon: MessageSquare };
    }
  };

  const filteredLogs = logs.filter(log => filterCode === 'ALL' || log.category_code === filterCode);

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Navbar onRefresh={fetchLogs} isRefreshing={loading} />

      <main className="flex-1 overflow-y-auto p-6 bg-aws-dark select-none">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
          <div>
            <h1 className="text-xl font-bold text-aws-gray flex items-center gap-2">
              <MessageSquare className="text-aws-orange" size={24} />
              COMMUNICATION ASSIST TIMELINE
            </h1>
            <p className="text-xs text-aws-gray/70 mt-1 uppercase font-mono">Non-verbal logs & physiological patterns</p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-mono text-aws-gray/70 uppercase">Filter:</span>
            <select
              value={filterCode}
              onChange={(e) => setFilterCode(e.target.value)}
              className="bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray px-3 py-1.5 focus:outline-none focus:border-aws-orange font-mono"
            >
              <option value="ALL">All need categories</option>
              <option value="HUNGER">Hunger Assists</option>
              <option value="RESTROOM">Restroom Requests</option>
              <option value="ANXIETY">Anxiety Indicators</option>
              <option value="DISCOMFORT">Discomfort Flags</option>
            </select>

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
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main timeline */}
          <div className="lg:col-span-8 glass-panel p-6 rounded-lg border border-aws-slate flex flex-col">
            <h2 className="text-sm font-bold text-aws-gray uppercase tracking-wider mb-6 border-b border-aws-slate pb-2">
              Assists Sequence Log
            </h2>

            {filteredLogs.length === 0 ? (
              <div className="text-center py-20 text-aws-gray/50 text-sm font-mono uppercase">
                No communication events recorded
              </div>
            ) : (
              <div className="relative border-l border-aws-slate ml-4 space-y-6">
                {filteredLogs.map((log) => {
                  const details = getCategoryDetails(log.category_code);
                  const Icon = details.icon;
                  return (
                    <div key={log.event_id} className="relative pl-8 group">
                      {/* Timeline dot */}
                      <div className="absolute -left-[9px] top-1.5 w-4 h-4 rounded-full bg-aws-navy border-2 border-aws-orange flex items-center justify-center z-10 group-hover:scale-110 transition-transform">
                        <div className="w-1.5 h-1.5 rounded-full bg-aws-orange" />
                      </div>

                      <div className="glass-panel p-4 rounded border border-aws-slate hover:border-aws-orange/30 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded border ${details.color}`}>
                            <Icon size={18} />
                          </div>
                          <div>
                            <h3 className="text-sm font-bold text-aws-gray uppercase font-mono">{details.label}</h3>
                            <p className="text-[10px] text-aws-gray/70 mt-0.5 uppercase font-mono">
                              Category Code: {log.category_code} | ID: {log.event_id.slice(0, 8)}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-1.5 text-xs font-mono text-aws-gray/70 bg-aws-navy/60 px-3 py-1.5 rounded border border-aws-slate w-fit">
                          <Calendar size={12} />
                          <span>{new Date(log.timestamp).toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Quick Insights card */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="glass-panel p-6 rounded-lg border border-aws-orange/15">
              <h2 className="text-xs font-bold text-aws-gray uppercase tracking-wider mb-4 border-b border-aws-slate pb-2">
                Need Frequency Insights
              </h2>
              
              <div className="space-y-4">
                {['HUNGER', 'RESTROOM', 'ANXIETY', 'DISCOMFORT'].map(code => {
                  const count = logs.filter(l => l.category_code === code).length;
                  const percent = logs.length > 0 ? (count / logs.length) * 100 : 0;
                  const details = getCategoryDetails(code);
                  const Icon = details.icon;
                  
                  return (
                    <div key={code} className="flex flex-col gap-1.5">
                      <div className="flex justify-between items-center text-xs font-mono">
                        <span className="text-aws-gray font-bold flex items-center gap-1.5 uppercase">
                          <Icon size={12} className="text-aws-orange" /> {code}
                        </span>
                        <span className="text-aws-gray/60 font-semibold">{count} presses ({percent.toFixed(0)}%)</span>
                      </div>
                      <div className="w-full bg-aws-navy h-1.5 rounded overflow-hidden">
                        <div 
                          className="bg-aws-orange h-full rounded" 
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="glass-panel p-6 rounded-lg border border-aws-slate font-mono text-[10px] text-aws-gray/70 space-y-3">
              <span className="block font-bold text-aws-teal uppercase">TIMELINE SYNC DATA</span>
              <span>Telemetry sync happens via AWS IoT Core MQTT need-code topic rules. Pushes are broadcast dynamically over persistent WebSockets.</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
export default CommAssistLogs;
