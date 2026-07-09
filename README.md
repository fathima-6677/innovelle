# AEGIS.SYS - Mission Critical Guardian System

**Status**: ✅ **OPERATIONAL** - Precision Data & Safety Logic Active  
**Version**: 3.3 - Enhanced Validation & 30% Warning System  
**Theme**: Precision Obsidian (Strict Data Validation + Elegant Overlays)

## 🛡️ System Overview

AEGIS.SYS is a real-time safety monitoring system with precision data validation, confirmation filters, and elegant 30% warning overlays. The system provides strict data validation, interactive tactical mapping, and professional emergency notifications.

### ⚡ Key Features

- **PRECISION DATA VALIDATION**: 5-second freshness check, "NOT CONNECTED" status for stale data
- **CONFIRMATION FILTER**: Fall alerts only trigger after 2 consecutive packets above 25.0 m/s²
- **30% WARNING OVERLAYS**: Elegant top-sheet alerts covering only 30% of screen
- **INTERACTIVE TACTICAL MAP**: Draggable, zoomable with long-press safe zone setting
- **SAFE ZONE MONITORING**: 100m radius geofence with violation alerts
- **AUDIO ALERT TESTING**: Debug button to verify TTS functionality
- **STRICT ACCEL LOGIC**: Only uses POSTed JSON payload data, no internal sensors
- **MCP STITCH INTEGRATION**: AI-powered UI design with professional overlays

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Configure your laptop IP in .env file
LAPTOP_IP=10.123.50.141
HARDWARE_DB_PATH=E:/Athidh/Autiguard/esp32-cloud-server-main/wearable.db
GOOGLE_MAPS_API_KEY=AIzaSyCZb9hp1XXwVnFm_cWBpHpQzw4J-FQUcOE
```

### 2. Backend Services (Enhanced Validation)
```bash
# Start precision-validated FastAPI backend
cd "sensor logger/ai-wearable/backend"
python main.py
# Server runs on: http://10.123.50.141:8000
# Features: 5-second data freshness, confirmation filters, strict validation
```

### 3. Mobile Data Simulation
```bash
# Start mobile sensor simulator (for demo)
python mobile_data_simulator.py
# Sends realistic sensor data to backend every 2 seconds
# Backend validates data freshness and applies confirmation filters
```

### 4. Flutter App (Enhanced UI)
```bash
cd autiguard_app
flutter run
# Features: 30% warning overlays, interactive maps, safe zone setting
# Long-press map to set safe zone, use TEST ALERTS button to verify audio
```

## 🎯 PRECISION ENHANCEMENTS

### Backend Validation
- **Data Freshness**: Returns "NOT CONNECTED" if no data received within 5 seconds
- **Confirmation Filter**: Fall detection requires 2 consecutive packets above 25.0 m/s²
- **Strict Accel Logic**: Only uses POSTed JSON accelerometer data, no internal sensors
- **Audio Trigger**: TTS alerts trigger exactly when noise_db > 85.0

### UI Improvements
- **30% Warning Overlays**: Elegant top-sheet notifications (Fall, Audio, Geofence)
- **Interactive Map**: Fully draggable and zoomable Google Maps
- **Safe Zone Setting**: Long-press map to set 100m radius safe zone
- **Distance Widget Removed**: Cleaner interface as requested
- **Test Alerts Button**: Debug functionality to verify audio system

### Safety Logic
- **Fall Detection**: Requires sustained acceleration > 25.0 m/s² for 2 packets
- **Audio Distress**: Triggers at exactly 85.0 dB with TTS notification
- **Geofence Violation**: Alerts when user moves outside 100m safe zone
- **Emergency Overlays**: Professional liquid glass design covering only 30% of screen
```

## 📊 API Endpoints

- **`GET /api/telemetry`**: Unified dual-source telemetry data
- **`POST /api/action`**: Action button requests (hunger, restroom, sos)
- **`POST /data`**: Mobile sensor data ingestion
- **`GET /`**: System status and documentation

## 🔧 Data Flow Architecture

```
Mobile Sensors → Simulator → FastAPI Backend → Global State → Flutter App
Hardware DB   → SQLite    → FastAPI Backend → Global State → Flutter App
```

### Live Data Processing
1. **Mobile Simulator** sends payload array with accelerometer, audio, GPS, steps
2. **SensorController** processes data and calculates safety thresholds
3. **Global State** stores live sensor values (accel_x, accel_y, accel_z, sound_db)
4. **Telemetry API** combines hardware + mobile data in unified JSON
5. **Flutter App** polls every 500ms and updates UI with live animations

## 🚨 Safety Logic

### Fall Detection
- **Threshold**: 25.0 m/s² (AEGIS system standard)
- **Calculation**: `magnitude = sqrt(x² + y² + z²)`
- **Response**: Massive "FALL DETECTED" overlay with emergency red pulsing

### Audio Distress
- **Threshold**: 85.0 dB (AEGIS system standard)
- **Response**: TTS alert "Safety Alert: High Noise Environment Detected"
- **Visual**: Audio warning indicators in status grid

### Action Buttons
- **🍔 HUNGER**: Sends hunger request to backend
- **🚽 RESTROOM**: Sends restroom request to backend  
- **🚨 SOS**: Triggers emergency SOS with visual confirmation

## 🎨 UI Components

### AEGIS Command Center
- **Header**: Professional AEGIS.SYS branding with neon cyan glow
- **Guardian Toggle**: Hardware/Mobile source selection
- **Vital Gauge**: Central animated gauge (BPM/Accelerometer)
- **Status Grid**: Fall Alert, Audio Distress, Panic Alert, Distance
- **Action Buttons**: Interactive buttons with animated checkmarks
- **Tactical Map**: Google Maps with dual markers and connection lines

### Glassmorphic Design
- **Theme**: Frosted Obsidian (high-contrast black & white)
- **Effects**: 25px blur BackdropFilter for glass cards
- **Animations**: Emergency red pulsing, heartbeat effects, smooth transitions
- **Typography**: Professional AEGIS font with outer glow effects

## 📱 Mobile Data Format

The mobile simulator sends data in SensorController-compatible format:

```json
{
  "payload": [
    {
      "name": "accelerometer",
      "values": {"x": -2.6, "y": 2.2, "z": 10.1}
    },
    {
      "name": "audio", 
      "values": {"db": 94.8}
    },
    {
      "name": "pedometer",
      "values": {"steps": 7696}
    },
    {
      "name": "location",
      "values": {"latitude": 13.0827, "longitude": 80.2707}
    }
  ]
}
```

## 🔍 Debug & Monitoring

### Backend Debug Output
```
DEBUG: Accel: 11.19 | X:-0.8 Y:-0.1 Z:11.2 | Steps: 2443 | Sound: 53 dB
🔊 AEGIS AUDIO DISTRESS: Sound level 94 dB > 85.0
🚨 AEGIS FALL DETECTED: Accel magnitude 27.3 > 25.0
```

### Mobile Simulator Output
```
✅ Data sent: Accel=11.19 | Steps=2443 | Sound=53.1dB
🔊 SIMULATING LOUD NOISE: 94.8 dB
🚨 SIMULATING FALL: 27.3 m/s²
```

## 🏆 Hackathon Achievements

- ✅ **Real-time Data Flow**: Fixed accelerometer latency issues
- ✅ **Live Safety Logic**: Fall detection and audio distress alerts operational
- ✅ **Professional UI**: AEGIS.SYS branding with glassmorphic design
- ✅ **Dual-Source Integration**: Hardware + Mobile unified telemetry
- ✅ **Emergency Systems**: Visual overlays, TTS alerts, action buttons
- ✅ **Google Maps Integration**: Live GPS tracking with tactical display
- ✅ **Flutter Performance**: 500ms polling with smooth animations

## 🔧 Troubleshooting

### Common Issues
1. **No accelerometer data**: Ensure mobile simulator is running and sending to correct IP
2. **API connection failed**: Check backend is running on port 8000
3. **Flutter build errors**: Run `flutter clean && flutter pub get`
4. **Map not loading**: Verify Google Maps API key in Android manifest

### System Requirements
- **Backend**: Python 3.8+, FastAPI, SQLite
- **Frontend**: Flutter 3.0+, Android SDK
- **Network**: All devices on same network with configured IP

---

**AEGIS.SYS Mission Status**: ✅ **COMPLETE & OPERATIONAL**  
**Ready for**: Hackathon demonstration, live safety monitoring, real-world deployment