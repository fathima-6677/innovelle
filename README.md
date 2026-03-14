# AUTIGUARD Emergency Monitoring System

A comprehensive emergency monitoring system with dual-source telemetry (hardware + mobile sensors), real-time communication, and WhatsApp emergency alerts.

## 🛡️ System Overview

AUTIGUARD is an emergency monitoring system designed for real-time safety monitoring with multiple data sources, fall detection, panic button integration, and automated emergency notifications via WhatsApp.

### ⚡ Key Features

- **Dual-Source Telemetry**: ESP32 hardware + mobile sensor integration
- **Real-time Communication**: Socket.IO WebSocket streaming (100ms intervals)
- **Emergency Detection**: Fall detection, panic button, audio distress alerts
- **WhatsApp Integration**: Automated emergency notifications via Twilio
- **Live Dashboard**: Flutter mobile app with tactical UI
- **Hardware Simulation**: Complete ESP32 simulator for testing

## 🚀 Quick Start

### 1. Environment Setup

Configure your environment variables in `.env`:

```bash
# Backend Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
LAPTOP_IP=10.123.50.141

# Twilio WhatsApp Integration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+918754617636
TWILIO_TEMPLATE_SID=HX350d429d32e64a552466cafecbe95f3c

# Hardware Database
HARDWARE_DB_PATH=E:\Athidh\Autiguard\database.db
```

### 2. Backend Server

```bash
cd "sensor logger/ai-wearable/backend"
pip install -r requirements.txt
python main.py
```

Server will start on `http://localhost:8001` with Socket.IO support.

### 3. Hardware Simulator

```bash
python simple_hardware_simulator.py
```

Simulates ESP32 wearable device sending BPM, panic button, and GPS data.

### 4. Flutter Mobile App

```bash
cd autiguard_app
flutter pub get
flutter run
```

## 📱 System Architecture

### Backend Components
- **FastAPI Server**: Main API server with Socket.IO integration
- **Serial Bridge**: COM3 serial communication for ESP32
- **Twilio Integration**: WhatsApp emergency notifications
- **SQLite Database**: Hardware telemetry storage
- **Real-time Streaming**: 100ms telemetry broadcasting

### Frontend Components
- **Flutter App**: Mobile emergency dashboard
- **Tactical UI**: High-contrast emergency interface
- **Real-time Updates**: Socket.IO client integration
- **Emergency Alerts**: Visual and audio notifications

### Hardware Integration
- **ESP32 Support**: Arduino Nano ESP32 compatibility
- **Serial Protocol**: `BPM:75,PANIC:0,STEPS:1240` format
- **WiFi Fallback**: Network-based data transmission
- **Hardware Simulation**: Complete testing environment

## 🔧 Emergency Detection

### Fall Detection
- **Threshold**: 11.0 m/s² acceleration magnitude
- **Latch Duration**: 10-second alert persistence
- **Multi-trigger**: Instant impact + freefall detection

### Audio Distress
- **Threshold**: 85.0 dB sound level
- **Alert Type**: "DISTRESS NOISE!" notification
- **Priority**: Shows before SOS in notification queue

### Panic Button
- **Hardware**: ESP32 physical button
- **Serial**: `PANIC:1` in data stream
- **Alert Type**: "PANIC BUTTON PRESSED!" notification

## 📡 Communication Protocol

### Socket.IO Events
- `telemetry_stream`: Real-time sensor data (100ms)
- `connection_status`: Client connection status
- `connect`/`disconnect`: Connection lifecycle

### REST API Endpoints
- `GET /api/telemetry`: Unified telemetry data
- `POST /api/hardware-data`: Hardware simulator data
- `POST /api/action`: Action button requests
- `GET /health`: Server health check

### WhatsApp Integration
- **Template-based**: Dynamic alert routing
- **Cooldown Protection**: 2-minute per alert type
- **Three Alert Types**: Critical Fall, Audio Distress, SOS Button

## 🎯 File Structure

```
autiguard/
├── autiguard_app/                 # Flutter mobile app
│   ├── lib/
│   │   ├── main.dart             # App entry point
│   │   ├── providers/            # State management
│   │   └── widgets/              # UI components
│   └── pubspec.yaml              # Flutter dependencies
├── sensor logger/ai-wearable/backend/  # Python backend
│   ├── main.py                   # FastAPI server
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables
│   └── api/                      # API routes
├── simple_hardware_simulator.py  # ESP32 simulator
├── aegis_esp32_serial_streamer.ino  # Arduino code
├── .env                          # Global environment
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 🔒 Security Features

- **Environment-based Configuration**: All credentials in .env files
- **CORS Protection**: Configured for Flutter app access
- **Input Validation**: Sanitized API inputs
- **Rate Limiting**: WhatsApp cooldown protection
- **Error Handling**: Graceful degradation on failures

## 🚀 Deployment

### Development
1. Start backend server: `python main.py`
2. Run hardware simulator: `python simple_hardware_simulator.py`
3. Launch Flutter app: `flutter run`

### Production
- Configure production environment variables
- Set up proper SSL certificates
- Configure Twilio production credentials
- Deploy backend to cloud service
- Build Flutter app for release

## 📞 Emergency Response

When an emergency is detected:
1. **Immediate UI Alert**: Visual notification in Flutter app
2. **WhatsApp Message**: Automated message to guardian
3. **Data Logging**: Emergency event stored in database
4. **Real-time Streaming**: Live telemetry to all connected clients
5. **Cooldown Protection**: Prevents spam notifications

## 🛠️ Development

### Backend Development
- Python 3.8+ required
- FastAPI framework
- Socket.IO for real-time communication
- SQLite for data persistence

### Frontend Development
- Flutter 3.0+ required
- Provider state management
- Socket.IO client integration
- Material Design components

### Hardware Development
- Arduino IDE for ESP32 programming
- Serial communication protocol
- WiFi network integration
- Sensor data formatting

---

**AUTIGUARD Mission Status**: ✅ **COMPLETE & OPERATIONAL**

**Ready for**: GitHub repository, live safety monitoring, emergency response deployment