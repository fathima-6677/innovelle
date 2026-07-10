import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { useAuthStore } from '../store/authStore';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { LineChart as ChartIcon, FileText, Download, TrendingUp, ShieldAlert, Award } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface TelemetryPoint {
  timestamp: string;
  heart_rate: number;
  stress_index: number;
  risk_level: string;
}

export const Reports: React.FC = () => {
  const { token } = useAuthStore();
  const [selectedWearerId, setSelectedWearerId] = useState<string>('');
  const [wearersList, setWearersList] = useState<any[]>([]);
  const [telemetryHistory, setTelemetryHistory] = useState<TelemetryPoint[]>([]);
  const [period, setPeriod] = useState<'weekly' | 'monthly'>('weekly');
  const [downloading, setDownloading] = useState(false);

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
    } catch (e) {
      const mock = [{ wearer_id: 'wearer-99', first_name: 'Aarav', last_name: 'Sharma' }];
      setWearersList(mock);
      setSelectedWearerId(mock[0].wearer_id);
    }
  };

  const fetchTelemetry = async () => {
    if (!selectedWearerId) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/telemetry/${selectedWearerId}?range=${period === 'weekly' ? '7d' : '30d'}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setTelemetryHistory(data);
      }
    } catch (e) {
      // Mock chart history
      const now = Date.now();
      const points: TelemetryPoint[] = [];
      const steps = period === 'weekly' ? 7 : 30;
      for (let i = steps; i >= 0; i--) {
        points.push({
          timestamp: new Date(now - i * 86400000).toISOString(),
          heart_rate: Math.floor(70 + Math.random() * 25),
          stress_index: Math.floor(20 + Math.random() * 50),
          risk_level: Math.random() > 0.8 ? 'ELEVATED' : 'NORMAL'
        });
      }
      setTelemetryHistory(points);
    }
  };

  const downloadReport = async (format: 'pdf' | 'csv') => {
    if (!selectedWearerId) return;
    setDownloading(true);
    try {
      const url = `${API_BASE_URL}/api/v1/reports/${selectedWearerId}?period=${period}&format=${format}`;
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = `autiguard_${period}_report_${selectedWearerId}.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (e) {
      alert("Failed to download report. Running in offline/development mock mode.");
    } finally {
      setDownloading(false);
    }
  };

  useEffect(() => {
    fetchWearers();
  }, []);

  useEffect(() => {
    fetchTelemetry();
  }, [selectedWearerId, period]);

  const chartData = telemetryHistory.map(pt => ({
    time: new Date(pt.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    Stress: pt.stress_index,
    HeartRate: pt.heart_rate
  }));

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Navbar />

      <main className="flex-1 overflow-y-auto p-6 bg-aws-dark select-none">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
          <div>
            <h1 className="text-xl font-bold text-black flex items-center gap-2">
              <ChartIcon className="text-aws-orange" size={24} />
              ANALYTICS & SAFETY REPORTS
            </h1>
            <p className="text-xs text-black/70 mt-1 uppercase font-mono">Export-ready PDF/CSV logs & clinical summaries</p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-mono text-black/70 uppercase">Period:</span>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value as any)}
              className="bg-aws-navy border border-aws-slate rounded text-sm text-black px-3 py-1.5 focus:outline-none focus:border-aws-orange font-mono"
            >
              <option value="weekly">Weekly View</option>
              <option value="monthly">Monthly View</option>
            </select>

            <select
              value={selectedWearerId}
              onChange={(e) => setSelectedWearerId(e.target.value)}
              className="bg-aws-navy border border-aws-slate rounded text-sm text-black px-3 py-1.5 focus:outline-none focus:border-aws-orange font-mono"
            >
              {wearersList.map(w => (
                <option key={w.wearer_id} value={w.wearer_id}>
                  {w.first_name} {w.last_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Quick analytics info */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="glass-panel p-4 rounded flex items-center gap-4 border-l-2 border-aws-orange">
            <div className="p-2 rounded bg-aws-orange/10 text-aws-orange">
              <TrendingUp size={20} />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-black/60 uppercase font-mono">Average Stress</span>
              <span className="text-sm font-bold text-black">
                {chartData.length > 0 ? (chartData.reduce((acc, curr) => acc + curr.Stress, 0) / chartData.length).toFixed(0) : '0'}%
              </span>
            </div>
          </div>

          <div className="glass-panel p-4 rounded flex items-center gap-4 border-l-2 border-aws-teal">
            <div className="p-2 rounded bg-aws-teal/10 text-aws-teal">
              <Award size={20} />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-black/60 uppercase font-mono">Avg Heart Rate</span>
              <span className="text-sm font-bold text-black">
                {chartData.length > 0 ? (chartData.reduce((acc, curr) => acc + curr.HeartRate, 0) / chartData.length).toFixed(0) : '0'} BPM
              </span>
            </div>
          </div>
        </div>

        {/* Charts and download console */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Recharts stress trend chart */}
          <div className="lg:col-span-8 glass-panel p-6 rounded-lg border border-aws-slate h-[380px] flex flex-col">
            <h2 className="text-xs font-bold text-black uppercase tracking-wider mb-4 border-b border-aws-slate pb-2">
              Stress & Heart Rate Trends
            </h2>

            <div className="flex-1 w-full text-xs">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="time" stroke="#232F3E" opacity={0.8} />
                  <YAxis stroke="#232F3E" opacity={0.8} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#EC7211', color: '#000000' }} />
                  <Line type="monotone" dataKey="Stress" stroke="#EC7211" strokeWidth={2.5} dot={{ r: 3 }} activeDot={{ r: 5 }} />
                  <Line type="monotone" dataKey="HeartRate" stroke="#007CA3" strokeWidth={2} dot={{ r: 2 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Export Action Card */}
          <div className="lg:col-span-4 glass-panel p-6 rounded-lg border border-aws-orange/15 flex flex-col justify-between">
            <div>
              <h2 className="text-xs font-bold text-black uppercase tracking-wider mb-4 border-b border-aws-slate pb-2 flex items-center gap-1.5">
                <FileText size={16} className="text-aws-orange" /> Report Center
              </h2>
              <p className="text-xs text-black/70 mb-6 font-mono">
                Download structured data summaries compliant with organization and clinical review frameworks.
              </p>

              <div className="space-y-3">
                <button
                  onClick={() => downloadReport('pdf')}
                  disabled={downloading}
                  className="w-full py-3 bg-aws-orange hover:bg-aws-orange/90 text-black font-bold text-xs rounded flex items-center justify-center gap-2 transition-all"
                >
                  <Download size={14} />
                  <span>{downloading ? 'Compiling PDF...' : 'Download PDF Report'}</span>
                </button>

                <button
                  onClick={() => downloadReport('csv')}
                  disabled={downloading}
                  className="w-full py-3 bg-aws-slate hover:bg-aws-slate/75 text-black border border-aws-orange/20 font-bold text-xs rounded flex items-center justify-center gap-2 transition-all"
                >
                  <Download size={14} />
                  <span>{downloading ? 'Compiling CSV...' : 'Download CSV Logs'}</span>
                </button>
              </div>
            </div>

            <div className="mt-6 border-t border-aws-slate pt-4 font-mono text-[9px] text-black/50">
              Report files generated securely. Enveloped fields decrypted temporarily for the duration of the stream.
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
export default Reports;
