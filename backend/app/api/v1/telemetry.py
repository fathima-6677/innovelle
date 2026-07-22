from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Header
from app.core.security import get_current_user
from app.core.dynamodb import db
from app.schemas.telemetry import TelemetryBatch, TelemetryItem
from app.services.geofence_service import geofence_service
from app.services.notification_service import notification_service
from app.services.dynamodb_sensor_service import sensor_db_service
from app.services.ml_service import ml_service
from pydantic import BaseModel
from typing import Optional
import datetime

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

# ── Fall Detection: consecutive spike tracker ─────────────────────────────────
# Stores the last reading that exceeded the 25 m/s² threshold per wearer.
# A fall alert fires only when TWO CONSECUTIVE packets both exceed the threshold.
_fall_spike_tracker: dict[str, bool] = {}   # wearer_id → was previous reading a spike?

async def process_ingested_readings(wearer_id: str, readings: list[TelemetryItem]):
    """Background task to evaluate falls, geofence breaches, and trigger notifications"""
    # 1. Fetch wearers geofences
    geofences = db.query_by_pk(f"WEARER#{wearer_id}", "GEOFENCE#")
    
    # 2. Fetch wearer profile (for contact escalation)
    wearer_profile = db.get_item(f"WEARER#{wearer_id}", "PROFILE")
    contacts = wearer_profile.get("emergency_contacts", []) if wearer_profile else []
    org_id = wearer_profile.get("org_id", "ORG#demo-org-99") if wearer_profile else "ORG#demo-org-99"

    for reading in readings:
        now_str = reading.timestamp.isoformat()
        
        # Save reading to database
        # TTL is 30 days
        ttl_val = int((reading.timestamp + datetime.timedelta(days=30)).timestamp())
        telemetry_db_item = {
            "PK": f"WEARER#{wearer_id}",
            "SK": f"TELEMETRY#{now_str}",
            "heart_rate": reading.heart_rate,
            "latitude": reading.latitude,
            "longitude": reading.longitude,
            "accel_x": reading.accel_x,
            "accel_y": reading.accel_y,
            "accel_z": reading.accel_z,
            "accel_magnitude": reading.accel_magnitude,
            "stress_index": reading.stress_index,
            "risk_level": reading.risk_level,
            "battery_level": reading.battery_level,
            "connectivity_status": reading.connectivity_status,
            "ttl": ttl_val
        }
        db.put_item(telemetry_db_item)

        # Broadcast telemetry to WebSocket
        from app.main import ws_manager
        await ws_manager.broadcast_to_org(org_id, {
            "wearer_id": wearer_id,
            "type": "telemetry",
            "timestamp": now_str,
            "heart_rate": reading.heart_rate,
            "stress_index": reading.stress_index,
            "risk_level": reading.risk_level,
            "battery_level": reading.battery_level,
            "latitude": reading.latitude,
            "longitude": reading.longitude
        })

        # A. Evaluate Geofence Breach
        for fence in geofences:
            if geofence_service.is_outside_geofence(reading.latitude, reading.longitude, fence):
                # Geofence breach! Create Alert
                alert_id = f"alert-geo-{int(datetime.datetime.utcnow().timestamp())}"
                alert_item = {
                    "PK": f"WEARER#{wearer_id}",
                    "SK": f"ALERT#{now_str}",
                    "GSI1PK": f"WEARER#{wearer_id}",
                    "GSI1SK": f"ALERT#geofence#{now_str}",
                    "alert_id": alert_id,
                    "wearer_id": wearer_id,
                    "wearer_name": wearer_profile.get("first_name", "Wearer") if wearer_profile else "Wearer",
                    "type": "geofence_breach",
                    "severity": "critical",
                    "details": {
                        "latitude": reading.latitude,
                        "longitude": reading.longitude,
                        "fence_name": fence.get("name", "Safe Zone"),
                        "message": f"Wearer breached safe zone: {fence.get('name')}"
                    },
                    "ack_status": "unacknowledged",
                    "timestamp": now_str
                }
                db.put_item(alert_item)
                
                # Broadcast alert to WebSocket
                await ws_manager.broadcast_to_org(org_id, {
                    "wearer_id": wearer_id,
                    "type": "alert"
                })
                
                # Dispatch notification
                for contact in contacts:
                    phone = contact.get("phone")
                    if phone:
                        notification_service.send_sms(
                            phone, 
                            f"ALERT: {alert_item['wearer_name']} left safe zone '{fence.get('name')}'."
                        )

        # B. Evaluate Fall Detection — requires 2 CONSECUTIVE packets > 25 m/s² (README spec)
        is_spike = reading.accel_magnitude > 25.0
        prev_was_spike = _fall_spike_tracker.get(wearer_id, False)
        _fall_spike_tracker[wearer_id] = is_spike  # update tracker for next packet

        if is_spike and prev_was_spike:
            # Two consecutive high-magnitude readings — confirmed fall event
            alert_id = f"alert-fall-{int(datetime.datetime.utcnow().timestamp())}"
            alert_item = {
                "PK": f"WEARER#{wearer_id}",
                "SK": f"ALERT#{now_str}",
                "GSI1PK": f"WEARER#{wearer_id}",
                "GSI1SK": f"ALERT#fall#{now_str}",
                "alert_id": alert_id,
                "wearer_id": wearer_id,
                "wearer_name": wearer_profile.get("first_name", "Wearer") if wearer_profile else "Wearer",
                "type": "fall_detected",
                "severity": "critical",
                "details": {
                    "magnitude": reading.accel_magnitude,
                    "message": "Critical impact fall detected!"
                },
                "ack_status": "unacknowledged",
                "timestamp": now_str
            }
            db.put_item(alert_item)
            
            # Broadcast alert to WebSocket
            await ws_manager.broadcast_to_org(org_id, {
                "wearer_id": wearer_id,
                "type": "alert"
            })
            
            # Dispatch notifications
            for contact in contacts:
                phone = contact.get("phone")
                if phone:
                    notification_service.send_sms(
                        phone, 
                        f"CRITICAL: Fall detected for {alert_item['wearer_name']}!"
                    )

@router.post("", status_code=status.HTTP_202_ACCEPTED)
def ingest_telemetry(payload: TelemetryBatch, background_tasks: BackgroundTasks,
                     x_device_api_key: str | None = Header(None, alias="X-Device-Api-Key")):
    """Batch ingest sensor readings from IoT device.
    Requires X-Device-Api-Key header matching the configured DEVICE_API_KEY.
    Executes safety analytics rules asynchronously."""
    from app.core.config import settings as app_settings
    if x_device_api_key != app_settings.DEVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing device API key. Include X-Device-Api-Key header."
        )
    background_tasks.add_task(process_ingested_readings, payload.wearer_id, payload.readings)
    return {"status": "accepted", "message": f"Processing {len(payload.readings)} telemetry points"}

@router.get("/{wearer_id}")
def get_telemetry(wearer_id: str, range: str = "24h", current_user: dict = Depends(get_current_user)):
    """Fetch historical telemetry readings for charts"""
    # Fetch all readings. In DynamoDB we query using partition key and filter SK prefix.
    # SK starts with TELEMETRY#
    raw_readings = db.query_by_pk(f"WEARER#{wearer_id}", "TELEMETRY#")
    
    # Filter based on time range (1h, 6h, 24h, 7d)
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(hours=24)
    if range == "1h":
        delta = datetime.timedelta(hours=1)
    elif range == "6h":
        delta = datetime.timedelta(hours=6)
    elif range == "7d":
        delta = datetime.timedelta(days=7)

    threshold_time = now - delta
    filtered_readings = []

    for item in raw_readings:
        timestamp_str = item.get("SK").replace("TELEMETRY#", "")
        try:
            item_time = datetime.datetime.fromisoformat(timestamp_str)
            if item_time >= threshold_time:
                filtered_readings.append({
                    "timestamp": timestamp_str,
                    "heart_rate": float(item.get("heart_rate", 0)),
                    "latitude": float(item.get("latitude", 0)),
                    "longitude": float(item.get("longitude", 0)),
                    "accel_magnitude": float(item.get("accel_magnitude", 0)),
                    "stress_index": float(item.get("stress_index", 0)),
                    "risk_level": item.get("risk_level", "NORMAL"),
                    "battery_level": float(item.get("battery_level", 100)),
                    "connectivity_status": item.get("connectivity_status", "CONNECTED")
                })
        except Exception:
            pass
            
    # Sort chronologically
    filtered_readings.sort(key=lambda x: x["timestamp"])
    return filtered_readings

# ── New Sensor Data Endpoints ─────────────────────────────────────────────────

class SensorDataResponse(BaseModel):
    device_id: str
    timestamp: int
    heart_rate: Optional[int] = None
    stress_score: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fall_detected: Optional[bool] = None
    sound_alert: Optional[bool] = None

@router.get("/latest/{device_id}", response_model=SensorDataResponse)
def get_telemetry_latest_by_device(device_id: str):
    """Fetch the absolute newest sensor reading from DynamoDB"""
    try:
        data = sensor_db_service.get_latest_sensor_data(device_id)
        if not data:
            raise HTTPException(status_code=404, detail="Sensor data not found")
        
        # ML Integration: Predict stress score if missing
        if data.get('stress_score') is None:
            hr = data.get('heart_rate', 70)
            score = ml_service.predict_stress(heart_rate=hr)
            if score is not None:
                data['stress_score'] = score
                sensor_db_service.update_stress_score(device_id, int(data['timestamp']), score)
                
        return data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Internal server error while fetching sensor data")

@router.get("/history/{device_id}", response_model=list[SensorDataResponse])
def get_telemetry_history_by_device(device_id: str):
    """Fetch recent sensor history (up to 100 items) from DynamoDB"""
    data = sensor_db_service.get_sensor_history(device_id, limit=100)
    return data
