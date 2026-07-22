import React from 'react';
import { Heart, Activity, AlertTriangle, Speaker, MapPin, Clock } from 'lucide-react';
import { TelemetryPoint } from '../services/telemetryService';

interface VitalsStripProps {
  currentData: TelemetryPoint | null;
}

export const VitalsStrip: React.FC<VitalsStripProps> = ({ currentData }) => {
  // Risk styling for Stress Score
  const stress = currentData?.stress_score ?? 0;
  const isSevere = stress > 80;
  const isElevated = stress > 65;

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

  const formatTime = (ts: string | number | undefined) => {
    if (!ts) return 'N/A';
    // If it's epoch seconds from DynamoDB, multiply by 1000
    const time = typeof ts === 'number' && ts < 10000000000 ? ts * 1000 : ts;
    return new Date(time).toLocaleTimeString();
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 mb-6">
      {/* Heart Rate Widget */}
      <div className="glass-panel p-3 rounded-lg flex flex-col justify-between h-24">
        <div className="flex items-center gap-1.5 text-[10px] text-aws-gray/50 uppercase font-semibold">
          <Heart size={12} className="text-red-500 animate-pulse" /> Heart Rate
        </div>
        <div className="text-xl font-bold font-mono text-aws-gray">
          {currentData?.heart_rate ? `${currentData.heart_rate} BPM` : 'N/A'}
        </div>
      </div>

      {/* SpO2 Widget (Mocked for now since not in DB) */}
      <div className="glass-panel p-3 rounded-lg flex flex-col justify-between h-24">
        <div className="flex items-center gap-1.5 text-[10px] text-aws-gray/50 uppercase font-semibold">
          <Activity size={12} className="text-blue-400" /> SpO₂
        </div>
        <div className="text-xl font-bold font-mono text-aws-gray">
          N/A
        </div>
      </div>

      {/* Stress Score Widget */}
      <div className={`glass-panel p-3 rounded-lg flex flex-col justify-between h-24 ${isSevere ? 'critical-glow-pulse' : ''}`}>
        <div className="flex items-center gap-1.5 text-[10px] text-aws-gray/50 uppercase font-semibold">
          <Activity size={12} className={riskColor} /> Stress Score
        </div>
        <div className="flex items-center gap-2">
          <div className={`text-xl font-bold font-mono ${riskColor}`}>
            {currentData?.stress_score ?? 0}
          </div>
          <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase font-mono tracking-wide ${riskBg} ${riskBorder} ${riskColor}`}>
            {isSevere ? 'HIGH' : isElevated ? 'ELEVATED' : 'NORMAL'}
          </span>
        </div>
      </div>

      {/* Fall Status */}
      <div className={`glass-panel p-3 rounded-lg flex flex-col justify-between h-24 ${currentData?.fall_detected ? 'bg-red-600/10 border-red-500/30' : ''}`}>
        <div className="flex items-center gap-1.5 text-[10px] text-aws-gray/50 uppercase font-semibold">
          <AlertTriangle size={12} className={currentData?.fall_detected ? 'text-red-500' : 'text-aws-gray'} /> Fall Status
        </div>
        <div className={`text-sm font-bold font-mono ${currentData?.fall_detected ? 'text-red-500 animate-pulse' : 'text-green-500'}`}>
          {currentData?.fall_detected ? 'FALL DETECTED' : 'SAFE'}
        </div>
      </div>

      {/* Sound Alert */}
      <div className={`glass-panel p-3 rounded-lg flex flex-col justify-between h-24 ${currentData?.sound_alert ? 'bg-red-600/10 border-red-500/30' : ''}`}>
        <div className="flex items-center gap-1.5 text-[10px] text-aws-gray/50 uppercase font-semibold">
          <Speaker size={12} className={currentData?.sound_alert ? 'text-red-500' : 'text-aws-gray'} /> Sound Alert
        </div>
        <div className={`text-sm font-bold font-mono ${currentData?.sound_alert ? 'text-red-500 animate-pulse' : 'text-green-500'}`}>
          {currentData?.sound_alert ? 'ALERT ACTIVE' : 'NORMAL'}
        </div>
      </div>

      {/* Coordinates (Lat/Lng) */}
      <div className="glass-panel p-3 rounded-lg flex flex-col justify-between h-24 col-span-2">
        <div className="flex items-center gap-1.5 text-[10px] text-aws-gray/50 uppercase font-semibold">
          <MapPin size={12} className="text-aws-teal" /> Location
        </div>
        <div className="text-sm font-bold font-mono text-aws-gray">
          {currentData?.latitude ? currentData.latitude.toFixed(6) : 'N/A'}, {currentData?.longitude ? currentData.longitude.toFixed(6) : 'N/A'}
        </div>
      </div>

      {/* Last Updated */}
      <div className="glass-panel p-3 rounded-lg flex flex-col justify-between h-24">
        <div className="flex items-center gap-1.5 text-[10px] text-aws-gray/50 uppercase font-semibold">
          <Clock size={12} className="text-aws-gray/70" /> Last Updated
        </div>
        <div className="text-xs font-bold font-mono text-aws-gray truncate">
          {formatTime(currentData?.timestamp)}
        </div>
      </div>
    </div>
  );
};
