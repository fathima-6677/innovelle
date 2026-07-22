import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { useAuthStore } from '../store/authStore';
import { telemetryService, TelemetryPoint } from '../services/telemetryService';
import { ShieldAlert, Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react';

interface DerivedAlert {
  id: string;
  timestamp: number;
  deviceId: string;
  alertType: string;
  heartRate: number | null;
  stressScore: number | null;
  location: string;
  status: 'ACTIVE' | 'RESOLVED';
}

export const AlertHistory: React.FC = () => {
  const { user } = useAuthStore();
  const [deviceId, setDeviceId] = useState('autiguard001');
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState<DerivedAlert[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('ALL');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchAndDeriveAlerts = async () => {
      setLoading(true);
      try {
        const history = await telemetryService.getTelemetryHistory(deviceId);
        const derived: DerivedAlert[] = [];
        
        history.forEach((point, index) => {
          const time = typeof point.timestamp === 'number' && point.timestamp < 10000000000 ? point.timestamp * 1000 : new Date(point.timestamp).getTime();
          const locStr = (point.latitude && point.longitude) ? `${point.latitude.toFixed(4)}, ${point.longitude.toFixed(4)}` : 'Unknown';
          
          if (point.heart_rate && point.heart_rate > 120) {
            derived.push({ id: `hr-${index}`, timestamp: time, deviceId: point.device_id, alertType: 'High Heart Rate', heartRate: point.heart_rate, stressScore: point.stress_score, location: locStr, status: 'RESOLVED' });
          }
          if (point.stress_score && point.stress_score > 80) {
            derived.push({ id: `str-${index}`, timestamp: time, deviceId: point.device_id, alertType: 'Critical Stress', heartRate: point.heart_rate, stressScore: point.stress_score, location: locStr, status: 'RESOLVED' });
          }
          if (point.fall_detected) {
            derived.push({ id: `fall-${index}`, timestamp: time, deviceId: point.device_id, alertType: 'Fall Detected', heartRate: point.heart_rate, stressScore: point.stress_score, location: locStr, status: 'RESOLVED' });
          }
          if (point.sound_alert) {
            derived.push({ id: `snd-${index}`, timestamp: time, deviceId: point.device_id, alertType: 'Sound Alert', heartRate: point.heart_rate, stressScore: point.stress_score, location: locStr, status: 'RESOLVED' });
          }
        });

        // Sort newest first
        derived.sort((a, b) => b.timestamp - a.timestamp);
        // Mark top 3 as active just for UI demonstration (since we derive from history, real status depends on ack_status in db, but we mock it here as resolved usually)
        derived.forEach((a, i) => { if (i < Math.min(derived.length, 2)) a.status = 'ACTIVE'; });
        setAlerts(derived);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAndDeriveAlerts();
  }, [deviceId]);

  // Apply filters and search
  const filteredAlerts = alerts.filter(a => {
    const matchesSearch = a.deviceId.toLowerCase().includes(searchTerm.toLowerCase()) || a.alertType.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'ALL' || a.alertType === filterType;
    return matchesSearch && matchesType;
  });

  // Pagination logic
  const totalPages = Math.ceil(filteredAlerts.length / itemsPerPage) || 1;
  const paginatedAlerts = filteredAlerts.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const uniqueTypes = ['ALL', ...Array.from(new Set(alerts.map(a => a.alertType)))];

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Navbar onRefresh={() => setCurrentPage(1)} isRefreshing={loading} />

      <main className="flex-1 overflow-y-auto p-6 bg-aws-dark">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
          <div>
            <h1 className="text-xl font-bold text-aws-gray flex items-center gap-2">
              <ShieldAlert className="text-red-500" size={24} />
              ALERT HISTORY & AUDIT LOG
            </h1>
            <p className="text-xs text-aws-gray/70 mt-1 uppercase font-mono">Historical safety triggers based on telemetry</p>
          </div>
        </div>

        {/* Controls */}
        <div className="glass-panel p-4 rounded-lg mb-6 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="flex flex-1 gap-4 w-full">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-aws-gray/50" size={16} />
              <input
                type="text"
                placeholder="Search alerts or device..."
                value={searchTerm}
                onChange={(e) => {setSearchTerm(e.target.value); setCurrentPage(1);}}
                className="w-full bg-aws-navy border border-aws-slate rounded pl-10 pr-4 py-2 text-sm text-aws-gray focus:border-aws-orange outline-none"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-aws-gray/50" size={16} />
              <select
                value={filterType}
                onChange={(e) => {setFilterType(e.target.value); setCurrentPage(1);}}
                className="bg-aws-navy border border-aws-slate rounded pl-10 pr-4 py-2 text-sm text-aws-gray focus:border-aws-orange outline-none appearance-none"
              >
                {uniqueTypes.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="glass-panel rounded-lg overflow-hidden border border-aws-slate">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-aws-gray">
              <thead className="bg-aws-navy text-xs uppercase font-mono text-aws-gray/60 border-b border-aws-slate">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Device ID</th>
                  <th className="px-4 py-3">Alert Type</th>
                  <th className="px-4 py-3">Heart Rate</th>
                  <th className="px-4 py-3">Stress Score</th>
                  <th className="px-4 py-3">Location</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-aws-slate">
                {loading ? (
                  <tr><td colSpan={7} className="px-4 py-8 text-center text-aws-gray/50 animate-pulse">Loading alert history...</td></tr>
                ) : paginatedAlerts.length === 0 ? (
                  <tr><td colSpan={7} className="px-4 py-8 text-center text-aws-gray/50">No alerts found matching criteria.</td></tr>
                ) : (
                  paginatedAlerts.map(alert => (
                    <tr key={alert.id} className="hover:bg-aws-navy/50 transition-colors">
                      <td className="px-4 py-3 font-mono">{new Date(alert.timestamp).toLocaleString()}</td>
                      <td className="px-4 py-3 font-mono text-aws-teal">{alert.deviceId}</td>
                      <td className="px-4 py-3">
                        <span className="font-semibold text-red-400">{alert.alertType}</span>
                      </td>
                      <td className="px-4 py-3 font-mono">{alert.heartRate ?? 'N/A'}</td>
                      <td className="px-4 py-3 font-mono">{alert.stressScore ?? 'N/A'}</td>
                      <td className="px-4 py-3 font-mono text-xs">{alert.location}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-[10px] uppercase font-bold tracking-wider ${alert.status === 'ACTIVE' ? 'bg-red-500/20 text-red-500 border border-red-500/30 animate-pulse' : 'bg-green-500/10 text-green-500 border border-green-500/20'}`}>
                          {alert.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="bg-aws-navy p-3 flex items-center justify-between border-t border-aws-slate text-xs text-aws-gray/60 font-mono">
            <div>
              Showing {filteredAlerts.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0} to {Math.min(currentPage * itemsPerPage, filteredAlerts.length)} of {filteredAlerts.length} entries
            </div>
            <div className="flex gap-2">
              <button 
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1 rounded bg-aws-dark border border-aws-slate hover:bg-aws-slate/20 disabled:opacity-50"
              >
                <ChevronLeft size={16} />
              </button>
              <button 
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-1 rounded bg-aws-dark border border-aws-slate hover:bg-aws-slate/20 disabled:opacity-50"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
