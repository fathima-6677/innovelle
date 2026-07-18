import React from 'react';
import { AlertCircle, AlertTriangle, ShieldAlert, Check, UserCheck } from 'lucide-react';

export interface AlertItemData {
  alert_id: string;
  wearer_id: string;
  wearer_name: string;
  type: string;
  severity: string;
  details: {
    message?: string;
    latitude?: number;
    longitude?: number;
    magnitude?: number;
    fence_name?: string;
  };
  ack_status: string;
  timestamp: string;
}

interface AlertFeedProps {
  alerts: AlertItemData[];
  onAcknowledge: (wearerId: string, alertId: string) => void;
}

export const AlertFeed: React.FC<AlertFeedProps> = ({ alerts, onAcknowledge }) => {
  const getSeverityStyles = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return {
          borderClass: 'border-l-4 border-l-red-600',
          bgClass: 'bg-red-600/5',
          textClass: 'text-red-500',
          icon: ShieldAlert,
        };
      case 'warning':
        return {
          borderClass: 'border-l-4 border-l-aws-orange',
          bgClass: 'bg-aws-orange/5',
          textClass: 'text-aws-orange',
          icon: AlertTriangle,
        };
      default:
        return {
          borderClass: 'border-l-4 border-l-aws-teal',
          bgClass: 'bg-aws-teal/5',
          textClass: 'text-aws-teal',
          icon: AlertCircle,
        };
    }
  };

  const getAlertReadableType = (type: string) => {
    switch (type) {
      case 'fall_detected':    return 'Critical Fall Impact';
      case 'geofence_breach':  return 'Geofence Safe Zone Breach';
      case 'panic_button':     return 'SOS Panic Alert Pressed';
      case 'qr_scan':          return 'Identity QR Scan Event';
      case 'audio_distress':   return 'High Noise / Distress Audio Alert';
      case 'battery_low':      return 'Low Battery Warning';
      case 'sos_panic':        return 'SOS Emergency Panic Button';
      default:                 return 'Safety Update Event';
    }
  };

  return (
    <div className="glass-panel p-6 rounded-lg select-none flex flex-col h-[400px]">
      <h2 className="text-sm font-bold text-aws-gray uppercase tracking-wider mb-4 border-b border-aws-slate pb-2">
        Active Command Center Alerts
      </h2>

      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {alerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-aws-gray/30 gap-2">
            <UserCheck size={36} className="opacity-50 text-aws-teal" />
            <span className="text-xs font-mono text-aws-gray/50">ALL SYSTEMS NORMAL — NO ALERTS IN QUEUE</span>
          </div>
        ) : (
          alerts.map((alert) => {
            const styles = getSeverityStyles(alert.severity);
            const AlertIcon = styles.icon;
            const isAck = alert.ack_status === 'acknowledged';

            return (
              <div
                key={alert.alert_id}
                className={`flex items-start justify-between p-4 rounded border border-aws-slate transition-all ${styles.borderClass} ${styles.bgClass} ${isAck ? 'opacity-40' : ''}`}
              >
                <div className="flex gap-3">
                  <AlertIcon className={`mt-0.5 ${styles.textClass}`} size={18} />
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-aws-gray">
                      {alert.wearer_name} — {getAlertReadableType(alert.type)}
                    </span>
                    <span className="text-xs text-aws-gray/80 mt-0.5">
                      {alert.details?.message || 'No description provided'}
                    </span>
                    <span className="text-[10px] text-aws-gray/60 font-mono mt-1">
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>

                {!isAck && (
                  <button
                    onClick={() => onAcknowledge(alert.wearer_id, alert.alert_id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-aws-slate hover:bg-aws-orange hover:text-white text-aws-orange text-xs font-semibold border border-aws-orange/30 transition-all ml-4"
                  >
                    <Check size={14} />
                    <span>Acknowledge</span>
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
