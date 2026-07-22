import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import { VitalsStrip } from '../components/VitalsStrip';
import { AlertFeed, AlertItemData } from '../components/AlertFeed';
import { CustomMapContainer } from '../components/MapContainer';
import { useAuthStore } from '../store/authStore';
import { Activity, ShieldAlert, User, WifiOff, Wifi, RefreshCw } from 'lucide-react';
import { API_BASE_URL } from '../config';
import { telemetryService, TelemetryPoint } from '../services/telemetryService';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export const Dashboard: React.FC = () => {
  const { user, token } = useAuthStore();
  // Set default to autiguard001 as per requirement
  const [selectedWearerId, setSelectedWearerId] = useState<string>('autiguard001');
  const [wearersList, setWearersList] = useState<any[]>([{ wearer_id: 'autiguard001', first_name: 'AutiGuard', last_name: 'Demo' }]);

  // Telemetry state
  const [currentTelemetry, setCurrentTelemetry] = useState<TelemetryPoint | null>(null);
  const [telemetryHistory, setTelemetryHistory] = useState<TelemetryPoint[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

  // Alerts state
  const [alerts, setAlerts] = useState<AlertItemData[]>([]);
  const [loading, setLoading] = useState(false);

  // Use refs for polling to avoid dependency cycle in useEffect
  const wearerIdRef = useRef(selectedWearerId);
  useEffect(() => {
    wearerIdRef.current = selectedWearerId;
  }, [selectedWearerId]);

  // Fetch Alerts List
  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/alerts`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAlerts(data.filter((a: any) => a.ack_status === 'unacknowledged'));
      }
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Initial Fetch History
  useEffect(() => {
    const fetchInitialHistory = async () => {
      try {
        const hist = await telemetryService.getTelemetryHistory(selectedWearerId);
        // Reverse so chronological order for charts
        setTelemetryHistory(hist.reverse());
        if (hist.length > 0) {
          setCurrentTelemetry(hist[hist.length - 1]);
        }
      } catch (err) {
        console.error("Failed to fetch initial history", err);
      }
    };
    fetchInitialHistory();
  }, [selectedWearerId]);

  // Polling Loop for Live Data
  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    const pollData = async () => {
      setIsRefreshing(true);
      try {
        const data = await telemetryService.getLatestTelemetry(wearerIdRef.current);
        if (data) {
          setCurrentTelemetry(data);
          setTelemetryHistory(prev => {
            // Append and keep last 100 points
            const newHistory = [...prev, data];
            // Sort by timestamp just in case
            newHistory.sort((a, b) => {
              const ta = typeof a.timestamp === 'number' ? a.timestamp : new Date(a.timestamp).getTime();
              const tb = typeof b.timestamp === 'number' ? b.timestamp : new Date(b.timestamp).getTime();
              return ta - tb;
            });
            // Simple deduplication based on timestamp
            const unique = new Map(newHistory.map(item => [item.timestamp, item]));
            return Array.from(unique.values()).slice(-100);
          });
          setConnectionStatus('connected');
        }
      } catch (err) {
        console.error("Polling error:", err);
        setConnectionStatus('disconnected');
      } finally {
        setIsRefreshing(false);
      }
    };

    // Poll immediately, then every 5 seconds
    pollData();
    intervalId = setInterval(pollData, 5000);

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, []);

  const handleAcknowledge = async (wearerId: string, alertId: string) => {
    setAlerts(prev => prev.filter(a => a.alert_id !== alertId));
  };

  const activeWearer = wearersList.find(w => w.wearer_id === selectedWearerId);
  const activeAlertsCount = alerts.length;

  // Chart data formatting
  const chartData = telemetryHistory.map(t => {
    const time = typeof t.timestamp === 'number' && t.timestamp < 10000000000 ? t.timestamp * 1000 : t.timestamp;
    return {
      time: new Date(time).toLocaleTimeString(),
      heartRate: t.heart_rate,
      stressScore: t.stress_score,
    }
  });

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Navbar onRefresh={() => fetchAlerts()} isRefreshing={isRefreshing || loading} />

      <main className="flex-1 overflow-y-auto p-6 bg-aws-dark">
        {/* Top Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
          <div>
            <h1 className="text-xl font-bold text-aws-gray flex items-center gap-2">
              <Activity className="text-aws-orange" size={24} />
              COMMAND CENTER LIVE DASHBOARD
            </h1>
            <p className="text-xs text-aws-gray/70 mt-1 uppercase font-mono">Real-time physiological &amp; safety console</p>
            {/* API connection status badge */}
            <div className="flex items-center gap-1.5 mt-1">
              {connectionStatus === 'connected' && (
                <span className="flex items-center gap-1 text-[10px] font-mono text-green-500"><Wifi size={10} /> API CONNECTED</span>
              )}
              {connectionStatus === 'connecting' && (
                <span className="flex items-center gap-1 text-[10px] font-mono text-aws-orange animate-pulse"><RefreshCw size={10} className="animate-spin" /> FETCHING DATA...</span>
              )}
              {connectionStatus === 'disconnected' && (
                <span className="flex items-center gap-1 text-[10px] font-mono text-red-500"><WifiOff size={10} /> API OFFLINE — RETRYING</span>
              )}
            </div>
          </div>

          {/* Wearer Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-aws-gray/70 uppercase">Active Wearer:</span>
            <select
              value={selectedWearerId}
              onChange={(e) => setSelectedWearerId(e.target.value)}
              className="bg-aws-navy border border-aws-slate rounded text-sm text-aws-gray px-3 py-1.5 focus:outline-none focus:border-aws-orange font-semibold font-mono"
            >
              {wearersList.map(w => (
                <option key={w.wearer_id} value={w.wearer_id}>
                  {w.first_name} {w.last_name} ({w.wearer_id})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Live Vitals strip */}
        {!currentTelemetry ? (
          <div className="w-full h-24 mb-6 flex items-center justify-center border border-aws-slate rounded text-aws-gray/50 animate-pulse bg-aws-navy">
            Loading telemetry data...
          </div>
        ) : (
          <VitalsStrip currentData={currentTelemetry} />
        )}

        {/* Main Grid: Map, Charts & Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Tactical Position Map */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            <div className="h-[400px]">
              {currentTelemetry?.latitude && currentTelemetry?.longitude ? (
                <CustomMapContainer
                  latitude={currentTelemetry.latitude}
                  longitude={currentTelemetry.longitude}
                  wearerName={activeWearer?.first_name}
                  deviceId={selectedWearerId}
                  heartRate={currentTelemetry.heart_rate}
                  stressScore={currentTelemetry.stress_score}
                />
              ) : (
                <div className="w-full h-full glass-panel flex items-center justify-center text-aws-gray/30 border border-aws-slate rounded">
                  Connecting To Device Stream GPS...
                </div>
              )}
            </div>

            {/* Historical Charts */}
            <div className="glass-panel p-4 rounded h-[300px]">
              <h2 className="text-sm font-bold text-aws-gray uppercase mb-4 flex items-center gap-2">
                <Activity size={16} className="text-aws-teal" /> Historical Telemetry Trends
              </h2>
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2B3648" />
                    <XAxis dataKey="time" stroke="#7A899F" tick={{ fontSize: 10 }} />
                    <YAxis yAxisId="left" stroke="#EC7211" tick={{ fontSize: 10 }} />
                    <YAxis yAxisId="right" orientation="right" stroke="#00A1C9" tick={{ fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#131A22', borderColor: '#2B3648', color: '#F2F3F3' }} />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Line yAxisId="left" type="monotone" name="Heart Rate (BPM)" dataKey="heartRate" stroke="#EC7211" strokeWidth={2} dot={false} isAnimationActive={false} />
                    <Line yAxisId="right" type="monotone" name="Stress Score" dataKey="stressScore" stroke="#00A1C9" strokeWidth={2} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="w-full h-full flex items-center justify-center text-aws-gray/40 text-xs">Awaiting historical data...</div>
              )}
            </div>
          </div>

          {/* Active alerts feed */}
          <div className="lg:col-span-4">
            <AlertFeed alerts={alerts} onAcknowledge={handleAcknowledge} />
          </div>
        </div>
      </main>
    </div>
  );
};
export default Dashboard;
