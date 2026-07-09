# 🛡️ AutiGuard & AEGIS.SYS: Cloud-Native Safety & Mission Critical Caregiver System

[![AWS Cloud](https://img.shields.io/badge/AWS-ap--south--1-FF9900?style=flat-square&logo=amazon-aws)](https://aws.amazon.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript-blue?style=flat-square&logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Containerized](https://img.shields.io/badge/Runtime-Docker%20%7C%20Rancher-2496ED?style=flat-square&logo=docker)](https://rancherdesktop.io/)
[![Security Grade](https://img.shields.io/badge/Security-AWS%20KMS%20PII%20Encryption-green?style=flat-square)](https://aws.amazon.com/kms/)

AutiGuard is a cloud-native, real-time safety and emotional monitoring platform designed to protect wearers and assist caregivers. Integrating live wearable telemetry, secure cloud infrastructure, and a premium glassmorphic control dashboard, the platform provides real-time distress detection, geofencing safety zones, and secure health profile management.

**AEGIS.SYS** (within this system) represents the mission-critical hardware, mobile simulator, and local validation subsystem featuring precision sensors, fall detection confirmation filters, and elegant 30% warning overlays.

* **System Status**: ✅ **OPERATIONAL** - Precision Data & Safety Logic Active  
* **System Version**: 3.3 - Enhanced Validation & 30% Warning System  
* **Theme**: Precision Obsidian (Strict Data Validation + Elegant Overlays)

---

## 🏗️ System Architecture & Data Flow

### Cloud-Native AWS Infrastructure
```mermaid
flowchart TD
    subgraph Client Application
        FE[React + Vite Frontend :5173]
    end

    subgraph API & Compute Layer
        BE[FastAPI Backend :8000]
        WS[WebSocket Manager]
    end

    subgraph AWS Security & Database Stack
        Cognito[Cognito User Pool]
        DynamoDB[(DynamoDB Single-Table)]
        KMS[KMS Envelope Key]
    end

    subgraph Telemetry Source
        Sim[Hardware Telemetry Simulator / AEGIS.SYS wearable]
    end

    Sim -->|Vitals / GPS Stream| BE
    BE <-->|Bidirectional Real-Time Data| WS
    WS <-->|Vitals & Warning Feeds| FE
    FE -->|SSO / Login Auth| Cognito
    BE -->|Token Validation & Groups| Cognito
    BE -->|Query & Insert Logs| DynamoDB
    BE -->|Encrypt / Decrypt PII Fields| KMS
```

### Local / Simulator Data Flow
```
Mobile Sensors → Simulator → FastAPI Backend → Global State → Flutter App/Web Frontend
Hardware DB   → SQLite    → FastAPI Backend → Global State → Flutter App/Web Frontend
```

### Deployed AWS Services
| Concern | AWS Service |
| :--- | :--- |
| **Device Ingestion** | AWS IoT Core (MQTT topics per device) |
| **Stream Processing** | Amazon Kinesis Data Streams + Firehose (raw archive to S3) |
| **Event-Driven Compute** | AWS Lambda (geofence checks, fall detection, alert dispatch) |
| **ML Model Hosting** | Amazon SageMaker (real-time endpoints) |
| **Primary Data Store** | Amazon DynamoDB (single-table design) |
| **Object Storage** | Amazon S3 (audio embeddings, reports, QR images) |
| **Auth** | Amazon Cognito (User Pools + Identity Pools, RBAC) |
| **API Layer** | Amazon API Gateway (REST + WebSocket) fronting FastAPI on ECS Fargate |
| **Secrets & Encryption** | AWS KMS + AWS Secrets Manager |
| **CDN / Hosting** | Amazon CloudFront + AWS Amplify Hosting |
| **IaC** | AWS CDK (TypeScript) |

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend (Web)** | React 18 (Vite), TypeScript, TailwindCSS, React Query, Zustand, Leaflet Maps, Recharts |
| **Mobile (AEGIS)** | Flutter 3.0+, Android SDK, Google Maps API |
| **Backend (Cloud)** | FastAPI (Python 3.11), Pydantic v2, PyJWT, Boto3, Uvicorn |
| **Local/Sim Backend** | Python 3.8+, FastAPI, SQLite |
| **Database** | Amazon DynamoDB (primary single-table design) & local SQLite (`wearable.db`) |
| **Containerization** | Docker, Docker Compose, Rancher Desktop (`nerdctl`) |
| **Infrastructure** | AWS CDK (TypeScript) |

---

## ⚡ Core Features & Precision Enhancements

### Cloud Security & Enterprise Core
* **Cognito-Powered RBAC**: Secure single sign-on (SSO) utilizing Cognito credentials flow. Roles (`org_admin`, `caregiver`) are checked against Cognito User Groups and decoded securely on the backend to enforce permission guards.
* **PII Envelope Encryption (AWS KMS)**: Sensitive wearer fields like `medical_notes`, `allergies`, and `medications` are encrypted on the backend using AWS KMS prior to DynamoDB persistence and decrypted on-the-fly only when requested by verified caregivers.
* **DynamoDB Single-Table Design**: High-efficiency schema optimization utilizing partition keys (`PK`), sort keys (`SK`), and a Global Secondary Index (`GSI1`) for O(1) retrieval of wearer profiles, telemetry, geofences, and alarms.
* **Real-Time WebSockets**: Live vitals (Heart Rate, Stress Index) and warnings are pushed dynamically to connected clients.
* **Liquid Glass Emergency Overlays**: Visually stunning dashboard alerting caregivers of critical incidents (falls, loud environments, geofence breaches) within a 30% screen sheet containing Text-to-Speech (TTS) emergency warnings.

### AEGIS.SYS Mission Critical Logic
* **PRECISION DATA VALIDATION**: 5-second freshness check on data streams, returning a "NOT CONNECTED" status for stale data.
* **CONFIRMATION FILTER**: Fall alerts only trigger after 2 consecutive packets exceed 25.0 m/s² acceleration.
* **30% WARNING OVERLAYS**: Elegant top-sheet notifications covering only 30% of the screen.
* **INTERACTIVE TACTICAL MAP**: Draggable, zoomable map with long-press safe zone setting (100m radius).
* **AUDIO ALERT TESTING**: Debug button to verify Text-to-Speech (TTS) functionality.
* **STRICT ACCEL LOGIC**: Only uses POSTed JSON payload data, ignoring internal sensors.

---

## 📊 Single-Table Data Model (AutiGuardCore)

| PK | SK | Entity | Attributes / Notes |
| :--- | :--- | :--- | :--- |
| `ORG#<orgId>` | `PROFILE` | Organization | Name, plan tier |
| `ORG#<orgId>` | `USER#<userId>` | Caregiver/Admin | Role, email, name |
| `WEARER#<wearerId>` | `PROFILE` | Wearer Profile | Name, DOB, encrypted medical notes, contacts |
| `WEARER#<wearerId>` | `TELEMETRY#<ISO8601>` | Telemetry logs | Heart rate, GPS coordinates, stress index, battery |
| `WEARER#<wearerId>` | `ALERT#<ISO8601>` | Alert event | Incident type, severity, acknowledgment status |
| `WEARER#<wearerId>` | `GEOFENCE#<fenceId>` | Geofence safe area| Coordinates, radius, state |

* **GSI1** Partition Key: `GSI1PK = WEARER#<wearerId>`, Sort Key: `GSI1SK = ALERT#<timestamp>` for querying historical wearer incidents efficiently.

---

## 📁 Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/       # Auth, wearers, telemetry, alerts, geofence, comms router
│   │   ├── core/         # Config settings, KMS security, DynamoDB wrapper
│   │   └── main.py       # FastAPI startup and WebSocket manager
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/              # React components, stores, maps, pages
│   ├── Dockerfile
│   └── package.json
├── infra/
│   ├── lib/              # AWS CDK Stacks (Compute, Database, Auth, Security)
│   └── tsconfig.json
├── autiguard_app/        # Flutter Client Application (AEGIS.SYS UI)
├── sensor logger/        # Hardware telemetry loggers & local server setup
│   └── ai-wearable/
├── assets/               # Production screenshots and graphics
└── docker-compose.yml    # Main orchestration docker compose config
```

---

## 🚀 Deployment & Local Setup

### 1. Cloud / Web Platform Local Setup
Configure the environment variables in `backend/.env`:
```env
AWS_DEFAULT_REGION=ap-south-1
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
DYNAMODB_TABLE=AutiGuardCore
COGNITO_USER_POOL_ID=ap-south-1_n9TxDAu3z
COGNITO_CLIENT_ID=3qu3kqqt4beqo1p6r02f8l1c09
KMS_KEY_ID=9d4d41d7-bf21-45b4-aae2-8f57d55c522e
MOCK_AWS=False
```

#### Run Locally (Without Containers)
```bash
# Start backend
cd backend
python -m venv venv
venv\Scripts\activate # source venv/bin/activate on Unix
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Start frontend
cd ../frontend
npm install
npm run dev
```

#### Run Containerized (Docker & Rancher Desktop)
```bash
# Using Docker
docker compose up --build -d

# Using Rancher Desktop (containerd runtime)
nerdctl compose up --build -d
```
Access the client dashboard at **`http://localhost:5173/`**.

#### Deploy to Rancher Kubernetes
```bash
# Build images in the local Kubernetes namespace
nerdctl --namespace k8s.io build -t autiguard-backend:latest ./backend
nerdctl --namespace k8s.io build -t autiguard-frontend:latest ./frontend

# Deploy manifests
kubectl apply -f kubernetes-deployment.yaml
```

---

### 2. AEGIS.SYS Local Hardware/Sim Setup
Configure the environment variables in the local root/hardware config:
```bash
# Configure your laptop IP in .env file
LAPTOP_IP=10.123.50.141
HARDWARE_DB_PATH=E:/Athidh/Autiguard/esp32-cloud-server-main/wearable.db
GOOGLE_MAPS_API_KEY=AIzaSyCZb9hp1XXwVnFm_cWBpHpQzw4J-FQUcOE
```

#### Run Backend Services (Enhanced Validation)
```bash
# Start precision-validated FastAPI backend
cd "sensor logger/ai-wearable/backend"
python main.py
# Server runs on: http://10.123.50.141:8000
# Features: 5-second data freshness, confirmation filters, strict validation
```

#### Run Mobile Data Simulation
```bash
# Start mobile sensor simulator (for demo)
python mobile_data_simulator.py
# Sends realistic sensor data to backend every 2 seconds
```

#### Run Flutter App (Enhanced UI)
```bash
cd autiguard_app
flutter run
# Features: 30% warning overlays, interactive maps, safe zone setting (long-press to set)
```

---

## 🚨 Safety & Event Ingestion Logic

### Fall Detection
* **Threshold**: 25.0 m/s² (AEGIS system standard)
* **Calculation**: `magnitude = sqrt(x² + y² + z²)`
* **Response**: "FALL DETECTED" overlay with emergency red pulsing. Triggered after 2 consecutive packets.

### Audio Distress
* **Threshold**: 85.0 dB (AEGIS system standard)
* **Response**: TTS alert: *"Safety Alert: High Noise Environment Detected"*

### Action Buttons
* **🍔 HUNGER**: Sends hunger request to backend.
* **🚽 RESTROOM**: Sends restroom request to backend.  
* **🚨 SOS**: Triggers emergency SOS with visual confirmation.

---

## 📊 API Endpoints (Local/AEGIS Backend)

* **`GET /api/telemetry`**: Unified dual-source telemetry data.
* **`POST /api/action`**: Action button requests (hunger, restroom, sos).
* **`POST /data`**: Mobile sensor data ingestion.
* **`GET /`**: System status and documentation.

---

## 📱 Mobile Data Format

The mobile simulator sends data in the following layout:
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

---

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

---

## 🏆 Verified Console Dashboard UI & Achievements

The caregiver console has been verified against the live AWS environment. Below is the active view showing the Leaflet mapping tracker, real-time stress index monitoring, and an active sound level distress incident:

![AutiGuard Control Console](assets/dashboard_screenshot.png)

### Hackathon Achievements
* **Real-time Data Flow**: Fixed accelerometer latency issues.
* **Live Safety Logic**: Fall detection and audio distress alerts fully operational.
* **Professional UI**: AEGIS.SYS branding with glassmorphic design.
* **Dual-Source Integration**: Hardware + Mobile unified telemetry.
* **Emergency Systems**: Visual overlays, TTS alerts, action buttons.
* **Google Maps Integration**: Live GPS tracking with tactical display.
* **Flutter Performance**: 500ms polling with smooth animations.

---

## 🔧 Troubleshooting & System Requirements

### Common Issues
1. **No accelerometer data**: Ensure mobile simulator is running and sending to correct IP.
2. **API connection failed**: Check backend is running on port 8000.
3. **Flutter build errors**: Run `flutter clean && flutter pub get`.
4. **Map not loading**: Verify Google Maps API key in Android manifest.

### System Requirements
* **Backend**: Python 3.8+, FastAPI, SQLite.
* **Frontend**: Flutter 3.0+, Android SDK.
* **Network**: All devices on the same network with correctly configured IPs.

---

**AEGIS.SYS Mission Status**: ✅ **COMPLETE & OPERATIONAL**  
**Ready for**: Hackathon demonstration, live safety monitoring, real-world deployment.
