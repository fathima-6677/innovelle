import React from 'react';
import { Heart, Activity, Battery, Wifi } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts';

interface TelemetryData {
  timestamp: string;
  heart_rate: number;
  stress_index: number;
  risk_level: string;
  battery_level: number;
  connectivity_status: string;
}

interface VitalsStripProps {
  currentData: TelemetryData | null;
  historyData: TelemetryData[];
}

export const VitalsStrip: React.FC<VitalsStripProps> = ({ currentData, historyData }) => {
  const heartRateHistory = historyData.map(h => ({ hr: h.heart_rate }));
  
  // Risk styling values
  const isSevere = currentData?.risk_level === 'SEVERE';
  const isElevated = currentData?.risk_level === 'ELEVATED';

  let riskColor = 'text-aws-teal';
  let riskBg = 'bg-aws-teal/10';
  let riskBorder = 'border-aws-teal/20';

  if (isSevere) {
    riskColor = 'text-red-500';
    riskBg = 'bg-red-600/10';
    riskBorder = 'border-red-500/30';
  } else if (isElevated) {
    riskColor = 'text-aws-orange';
    riskBg = 'bg-aws-orange/10';
    riskBorder = 'border-aws-orange/30';
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {/* Heart Rate Widget */}
      <div className="glass-panel p-4 rounded-lg flex flex-col justify-between h-32 relative overflow-hidden">
        <div className="flex items-center justify-between text-xs text-aws-gray/50 uppercase font-semibold">
          <span className="flex items-center gap-1.5"><Heart size={14} className="text-red-500 animate-pulse" /> Heart Rate</span>
          <span className="text-aws-gray font-mono">{currentData?.heart_rate ? `${currentData.heart_rate} BPM` : 'N/A'}</span>
        </div>
        
        {/* Heart Rate Mini Trendline */}
        <div className="h-12 w-full mt-2">
          {heartRateHistory.length > 1 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={heartRateHistory}>
                <YAxis domain={['dataMin - 5', 'dataMax + 5']} hide />
                <Line type="monotone" dataKey="hr" stroke="#E63946" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-xs text-aws-gray/50">Awaiting Sensor Logs...</div>
          )}
        </div>
      </div>

      {/* Stress Index Gauge Widget */}
      <div className={`glass-panel p-4 rounded-lg flex flex-col justify-between h-32 relative ${isSevere ? 'critical-glow-pulse' : ''}`}>
        <div className="flex items-center justify-between text-xs text-aws-gray/50 uppercase font-semibold">
          <span className="flex items-center gap-1.5"><Activity size={14} className={riskColor} /> Stress Index</span>
          <span className={`font-bold font-mono ${riskColor}`}>{currentData?.stress_index ?? 0}%</span>
        </div>

        <div className="mt-3 flex items-center justify-between gap-4">
          <div className="flex-1 bg-aws-slate h-3 rounded-full overflow-hidden border border-aws-gray/5">
            <div 
              className={`h-full transition-all duration-1000 ${
                isSevere ? 'bg-red-500' : isElevated ? 'bg-aws-orange' : 'bg-aws-teal'
              }`}
              style={{ width: `${currentData?.stress_index ?? 0}%` }}
            />
          </div>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase font-mono tracking-wide ${riskBg} ${riskBorder} ${riskColor}`}>
            {currentData?.risk_level ?? 'NORMAL'}
          </span>
        </div>
        <span className="text-[10px] text-aws-gray/30 mt-1">Calculated via AWS SageMaker Real-time Endpoint</span>
      </div>

      {/* Battery Status Widget */}
      <div className="glass-panel p-4 rounded-lg flex flex-col justify-between h-32">
        <div className="flex items-center justify-between text-xs text-aws-gray/50 uppercase font-semibold">
          <span className="flex items-center gap-1.5"><Battery size={14} className="text-green-500" /> Battery Level</span>
          <span className="text-aws-gray font-mono">{currentData?.battery_level ? `${currentData.battery_level}%` : 'N/A'}</span>
        </div>
        <div className="flex items-center gap-3 mt-4">
          <div className="w-12 h-6 border-2 border-aws-slate rounded p-0.5 flex relative">
            <div 
              className={`h-full rounded-sm ${
                (currentData?.battery_level ?? 100) < 25 ? 'bg-red-500' : 'bg-green-500'
              }`}
              style={{ width: `${currentData?.battery_level ?? 100}%` }}
            />
            <div className="w-1 h-2 bg-aws-slate absolute -right-1.5 top-1.5 rounded-r-sm" />
          </div>
          <span className="text-xs text-aws-gray/60 font-mono">
            {(currentData?.battery_level ?? 100) < 25 ? 'Low Battery Alert' : 'Charging Status Normal'}
          </span>
        </div>
      </div>

      {/* Connectivity Status Widget */}
      <div className="glass-panel p-4 rounded-lg flex flex-col justify-between h-32">
        <div className="flex items-center justify-between text-xs text-aws-gray/50 uppercase font-semibold">
          <span className="flex items-center gap-1.5"><Wifi size={14} className="text-aws-teal" /> Network Status</span>
          <span className="text-aws-gray font-mono uppercase">{currentData?.connectivity_status ?? 'DISCONNECTED'}</span>
        </div>
        <div className="flex items-center gap-2 mt-4">
          <Wifi size={24} className={currentData?.connectivity_status === 'CONNECTED' ? 'text-green-500 animate-pulse' : 'text-aws-slate'} />
          <span className="text-xs font-mono text-aws-gray/60">
            {currentData?.connectivity_status === 'CONNECTED' ? 'Ingesting via AWS IoT Core' : 'Stale Data / Wearer Offline'}
          </span>
        </div>
      </div>
    </div>
  );
};
