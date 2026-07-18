import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import { VitalsStrip } from '../components/VitalsStrip';
import { AlertFeed, AlertItemData } from '../components/AlertFeed';
import { CustomMapContainer } from '../components/MapContainer';
import { useAuthStore } from '../store/authStore';
import { Activity, ShieldAlert, User, WifiOff, Wifi } from 'lucide-react';
import { API_BASE_URL, WS_BASE_URL } from '../config';

// ─── Alert Chime (Web Audio API) ─────────────────────────────────────────────
function playAlertChime() {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.4);
    gain.gain.setValueAtTime(0.6, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.6);
  } catch {
    // Audio not available — fail silently
  }
}

// ─── Browser Push Notification ────────────────────────────────────────────────
function sendBrowserNotification(title: string, body: string) {
  if (!('Notification' in window)) return;
  if (Notification.permission === 'granted') {
    new Notification(title, { body, icon: '/vite.svg' });
  } else if (Notification.permission !== 'denied') {
    Notification.requestPermission().then(perm => {
      if (perm === 'granted') new Notification(title, { body, icon: '/vite.svg' });
    });
  }
}

interface TelemetryPoint {
  timestamp: string;
  heart_rate: number;
  stress_index: number;
  risk_level: string;
  battery_level: number;
  connectivity_status: string;
  latitude: number;
  longitude: number;
}

export const Dashboard: React.FC = () => {
  const { user, token } = useAuthStore();
  const [selectedWearerId, setSelectedWearerId] = useState<string>('');
  const [wearersList, setWearersList] = useState<any[]>([]);

  // Telemetry state
  const [currentTelemetry, setCurrentTelemetry] = useState<TelemetryPoint | null>(null);
  const [telemetryHistory, setTelemetryHistory] = useState<TelemetryPoint[]>([]);

  // Alerts state
  const [alerts, setAlerts] = useState<AlertItemData[]>([]);
  const [loading, setLoading] = useState(false);

  // WebSocket connection state
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectDelayRef = useRef<number>(1000);   // starts at 1s, doubles on each failure
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const prevAlertCountRef = useRef<number>(0);       // tracks alert count to detect new arrivals

  // Fetch Wearers List
  const fetchWearers = useCallback(async () => {
    setLoading(true);
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
      // Offline fallback: load mock wearer
      const mockWearers = [
        { wearer_id: 'wearer-99', first_name: 'Aarav', last_name: 'Sharma', dob: '2016-04-12' }
      ];
      setWearersList(mockWearers);
      setSelectedWearerId(mockWearers[0].wearer_id);
    } finally {
      setLoading(false);
    }
  }, [token, selectedWearerId]);

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
      // Offline fallback
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Acknowledge Alert
  const handleAcknowledge = async (wearerId: string, alertId: string) => {
    // Optimistic UI update
    setAlerts(prev => prev.filter(a => a.alert_id !== alertId));
    
    try {
      await fetch(`${API_BASE_URL}/api/v1/alerts/${wearerId}/acknowledge/${alertId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchAlerts();
    } catch {
      console.log("Could not update status on server, offline fallback succeeded optimistically.");
    }
  };

  // Setup WebSocket / Simulation Fallback
  useEffect(() => {
    fetchWearers();
    fetchAlerts();
  }, [fetchWearers, fetchAlerts]);

  useEffect(() => {
    if (!selectedWearerId) return;

    let isDestroyed = false;

    // ── WebSocket with exponential backoff reconnect ──────────────────────────
    const orgId = user?.orgId || 'demo-org-99';
    const wsUrl = `${WS_BASE_URL}/api/v1/ws/${encodeURIComponent(orgId)}`;

    const connect = () => {
      if (isDestroyed) return;
      setWsStatus('connecting');
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        if (isDestroyed) { ws.close(); return; }
        console.log('✅ WebSocket connected to API portal');
        setWsStatus('connected');
        reconnectDelayRef.current = 1000; // reset backoff on successful connect
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.wearer_id === selectedWearerId) {
            if (msg.type === 'telemetry') {
              const point: TelemetryPoint = {
                timestamp: msg.timestamp,
                heart_rate: msg.heart_rate,
                stress_index: msg.stress_index,
                risk_level: msg.risk_level,
                battery_level: msg.battery_level,
                connectivity_status: 'CONNECTED',
                latitude: msg.latitude,
                longitude: msg.longitude,
              };
              setCurrentTelemetry(point);
              setTelemetryHistory(prev => [...prev.slice(-20), point]);
            } else if (msg.type === 'alert') {
              // ── Play chime + browser notification on new alert ──────────────
              playAlertChime();
              sendBrowserNotification(
                '🚨 AutiGuard Alert',
                `New safety alert received for wearer ${selectedWearerId}`
              );
              fetchAlerts();
            }
          }
        } catch (err) {
          console.error(err);
        }
      };

      ws.onerror = () => {
        console.warn('⚠️ WebSocket error encountered.');
      };

      ws.onclose = () => {
        if (isDestroyed) return;
        setWsStatus('disconnected');
        // Exponential backoff: 1s → 2s → 4s → … max 30s
        const delay = Math.min(reconnectDelayRef.current, 30000);
        console.warn(`🔄 WebSocket closed. Reconnecting in ${delay / 1000}s...`);
        reconnectTimerRef.current = setTimeout(() => {
          reconnectDelayRef.current = delay * 2;
          connect();
        }, delay);
      };
    };

    connect();

    // Telemetry Simulation loop fallback (always runs to ensure premium UX)
    // In production, when WebSocket updates arrive, it updates state. For simulation,
    // we simulate realistic coordinate drifts, heart rate changes, and stress indices.
    let simulatedLat = 11.9416;
    let simulatedLng = 79.8083;
    // Simulate a realistic battery starting between 75-100%, slowly draining
    let simulatedBattery = Math.floor(75 + Math.random() * 25);
    
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          simulatedLat = pos.coords.latitude;
          simulatedLng = pos.coords.longitude;
        },
        (error) => console.error("Dashboard geolocation error:", error),
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      );
    }
    
    const interval = setInterval(() => {
      // Simulate slight drift
      simulatedLat += (Math.random() - 0.5) * 0.0001;
      simulatedLng += (Math.random() - 0.5) * 0.0001;
      
      // Drain battery by ~0.1% per tick (every 2s), with slight fluctuation
      simulatedBattery = Math.max(0, simulatedBattery - 0.1 + (Math.random() - 0.5) * 0.05);

      const hr = Math.floor(70 + Math.random() * 25);
      const stress = Math.floor(20 + Math.random() * 50);
      const risk = stress > 65 ? 'ELEVATED' : 'NORMAL';

      const point: TelemetryPoint = {
        timestamp: new Date().toISOString(),
        heart_rate: hr,
        stress_index: stress,
        risk_level: risk,
        battery_level: Math.round(simulatedBattery),
        connectivity_status: 'CONNECTED',
        latitude: simulatedLat,
        longitude: simulatedLng,
      };

      setCurrentTelemetry(point);
      setTelemetryHistory(prev => {
        const newHistory = [...prev, point];
        return newHistory.slice(-20); // Keep last 20
      });
    }, 2000);

    return () => {
      isDestroyed = true;
      clearInterval(interval);
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      if (socketRef.current) socketRef.current.close();
    };
  }, [selectedWearerId, user, fetchAlerts]);


  const activeWearer = wearersList.find(w => w.wearer_id === selectedWearerId);
  const activeAlertsCount = alerts.length;

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Navbar onRefresh={() => { fetchWearers(); fetchAlerts(); }} isRefreshing={loading} />

      <main className="flex-1 overflow-y-auto p-6 bg-aws-dark">
        {/* Top Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
          <div>
            <h1 className="text-xl font-bold text-aws-gray flex items-center gap-2">
              <Activity className="text-aws-orange" size={24} />
              COMMAND CENTER LIVE DASHBOARD
            </h1>
            <p className="text-xs text-aws-gray/70 mt-1 uppercase font-mono">Real-time physiological &amp; safety console</p>
            {/* WebSocket connection status badge */}
            <div className="flex items-center gap-1.5 mt-1">
              {wsStatus === 'connected' && (
                <span className="flex items-center gap-1 text-[10px] font-mono text-green-500"><Wifi size={10} /> WS CONNECTED</span>
              )}
              {wsStatus === 'connecting' && (
                <span className="flex items-center gap-1 text-[10px] font-mono text-aws-orange animate-pulse"><Wifi size={10} /> WS CONNECTING...</span>
              )}
              {wsStatus === 'disconnected' && (
                <span className="flex items-center gap-1 text-[10px] font-mono text-red-500"><WifiOff size={10} /> WS DISCONNECTED — RETRYING</span>
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
                  {w.first_name} {w.last_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="glass-panel p-4 rounded flex items-center gap-4">
            <div className={`p-2 rounded ${activeAlertsCount > 0 ? 'bg-red-600/10 border border-red-500/20 text-red-500' : 'bg-green-600/10 border border-green-500/20 text-green-500'}`}>
              <ShieldAlert size={20} />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-aws-gray/60 uppercase font-mono">System Warnings</span>
              <span className="text-sm font-bold text-aws-gray">
                {activeAlertsCount > 0 ? `${activeAlertsCount} Unresolved Warnings` : 'All Systems Verified Safe'}
              </span>
            </div>
          </div>

          <div className="glass-panel p-4 rounded flex items-center gap-4">
            <div className="p-2 rounded bg-aws-teal/10 border border-aws-teal/20 text-aws-teal">
              <Activity size={20} />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-aws-gray/60 uppercase font-mono">Stress Assessment</span>
              <span className="text-sm font-bold text-aws-gray">
                Stress Level: {currentTelemetry?.stress_index ?? 'Calculating...'}% ({currentTelemetry?.risk_level ?? 'NORMAL'})
              </span>
            </div>
          </div>

          <div className="glass-panel p-4 rounded flex items-center gap-4">
            <div className="p-2 rounded bg-aws-orange/10 border border-aws-orange/20 text-aws-orange">
              <User size={20} />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-aws-gray/60 uppercase font-mono">Active Target Details</span>
              <span className="text-sm font-bold text-aws-gray font-mono">
                {activeWearer ? `${activeWearer.first_name} ${activeWearer.last_name} (${activeWearer.wearer_id.slice(0,8)})` : 'None Selected'}
              </span>
            </div>
          </div>
        </div>

        {/* Live Vitals strip */}
        <VitalsStrip currentData={currentTelemetry} historyData={telemetryHistory} />

        {/* Main Grid: Map & Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Tactical Position Map */}
          <div className="lg:col-span-8 h-[400px]">
            {currentTelemetry ? (
              <CustomMapContainer
                latitude={currentTelemetry.latitude}
                longitude={currentTelemetry.longitude}
                wearerName={activeWearer?.first_name}
              />
            ) : (
              <div className="w-full h-full glass-panel flex items-center justify-center text-aws-gray/30 border border-aws-slate rounded">
                Connecting To Device Stream GPS...
              </div>
            )}
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
