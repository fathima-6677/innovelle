from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import router as auth_router
from app.api.v1.wearers import router as wearers_router
from app.api.v1.telemetry import router as telemetry_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.geofence import router as geofence_router
from app.api.v1.qr import router as qr_router
from app.api.v1.ml import router as ml_router
from app.api.v1.comms import router as comms_router
from app.api.v1.reports import router as reports_router
from app.core.config import settings
import json

app = FastAPI(
    title="AutiGuard API Portal",
    description="AWS-Native AI Safety & Emotional Monitoring Backend Portal",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under API v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(wearers_router, prefix="/api/v1")
app.include_router(telemetry_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(geofence_router, prefix="/api/v1")
app.include_router(qr_router, prefix="/api/v1") # Includes /qr/resolve at root via custom tags/routes
app.include_router(ml_router, prefix="/api/v1")
app.include_router(comms_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")

# WebSocket Connection Manager for Real-time Dashboard Updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, org_id: str, websocket: WebSocket):
        await websocket.accept()
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []
        self.active_connections[org_id].append(websocket)
        print(f"[WS] WebSocket client connected to Org: {org_id}")

    def disconnect(self, org_id: str, websocket: WebSocket):
        if org_id in self.active_connections:
            self.active_connections[org_id].remove(websocket)
            if not self.active_connections[org_id]:
                del self.active_connections[org_id]
        print(f"[WS] WebSocket client disconnected from Org: {org_id}")

    async def broadcast_to_org(self, org_id: str, message: dict):
        if org_id in self.active_connections:
            for connection in self.active_connections[org_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error sending socket message: {e}")

ws_manager = ConnectionManager()

@app.websocket("/api/v1/ws/{org_id}")
async def websocket_endpoint(websocket: WebSocket, org_id: str):
    """Real-time updates websocket channel per organization"""
    await ws_manager.connect(org_id, websocket)
    try:
        while True:
            # Maintain connection alive, receive client acknowledgements or heartbeat
            data = await websocket.receive_text()
            # Process optional inbound instructions from client
            payload = json.loads(data)
            await websocket.send_text(json.dumps({"status": "heartbeat_ack", "received": payload}))
    except WebSocketDisconnect:
        ws_manager.disconnect(org_id, websocket)
    except Exception as e:
        print(f"WebSocket processing error: {e}")
        ws_manager.disconnect(org_id, websocket)

from app.core.security import encrypt_field
import datetime

@app.on_event("startup")
def startup_event():
    if settings.MOCK_AWS:
        from app.core.dynamodb import db
        profile = db.get_item("WEARER#wearer-99", "PROFILE")
        if not profile:
            print("[STARTUP] Populating Mock DynamoDB Store with sample data...")
            now = datetime.datetime.utcnow().isoformat()
            
            # Encrypt fields
            notes = encrypt_field("Sensitive to loud noises and bright lights.")
            allergies = encrypt_field("Peanuts")
            meds = encrypt_field("None")
            
            # Put Wearer Profile
            wearer_item = {
                "PK": "WEARER#wearer-99",
                "SK": "PROFILE",
                "wearer_id": "wearer-99",
                "org_id": "ORG#demo-org-99",
                "first_name": "Aarav",
                "last_name": "Sharma",
                "dob": "2016-04-12",
                "medical_notes": notes,
                "allergies": allergies,
                "medications": meds,
                "qr_tiering_rules": {"medical": "public", "contacts": "auth_only"},
                "emergency_contacts": [{"name": "Dad", "phone": "+919629455996"}],
                "created_at": now
            }
            db.put_item(wearer_item)
            
            # Link to Org
            linkage_item = {
                "PK": "ORG#demo-org-99",
                "SK": "WEARER#wearer-99",
                "wearer_id": "wearer-99",
                "created_at": now
            }
            db.put_item(linkage_item)
            
            # Put Geofence
            fence_item = {
                "PK": "WEARER#wearer-99",
                "SK": "GEOFENCE#fence-99",
                "fence_id": "fence-99",
                "wearer_id": "wearer-99",
                "name": "Home Safe Area",
                "type": "radius",
                "coordinates": [{"lat": 11.9416, "lng": 79.8083}],
                "radius_meters": 150,
                "is_active": True
            }
            db.put_item(fence_item)
            
            # Put Alert
            alert_id = "alert-demo-1"
            alert_item = {
                "PK": "WEARER#wearer-99",
                "SK": f"ALERT#{now}",
                "GSI1PK": "WEARER#wearer-99",
                "GSI1SK": f"ALERT#demo-alert#{now}",
                "alert_id": alert_id,
                "wearer_id": "wearer-99",
                "wearer_name": "Aarav Sharma",
                "type": "audio_distress",
                "severity": "warning",
                "details": {"message": "High sound levels (88.5 dB) detected", "sound_level_db": 88.5},
                "ack_status": "unacknowledged",
                "timestamp": now
            }
            db.put_item(alert_item)
            print("[OK] Mock database initialized with sample wearer Aarav Sharma.")

@app.get("/")
def health_check():
    # Trigger uvicorn reload to load updated .env variables
    """System Health Check Endpoint"""
    return {
        "status": "operational",
        "service": "AutiGuard API Engine",
        "aws_mode": "mock" if settings.MOCK_AWS else "production",
        "dynamodb_table": settings.DYNAMODB_TABLE
    }
