from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

router = APIRouter(tags=["sensor"])

# Initialize DynamoDB client (boto3)
# We use boto3 directly since the new table AutiGuardSensorData is distinct from the primary Core table.
dynamodb = boto3.resource(
    'dynamodb',
    region_name=settings.AWS_REGION if hasattr(settings, 'AWS_REGION') else 'ap-south-1'
)
table_name = "AutiGuardSensorData"

def get_table():
    return dynamodb.Table(table_name)

@router.get("/sensor/latest")
def get_sensor_latest(device_id: str):
    """Fetches the most recent sensor reading for a device."""
    table = get_table()
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('device_id').eq(device_id),
            ScanIndexForward=False, # Sort descending by timestamp
            Limit=1
        )
        items = response.get('Items', [])
        if not items:
            return {"message": "No sensor data found for device.", "data": None}
        return {"data": items[0]}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sensor/history")
def get_sensor_history(device_id: str, limit: int = 50):
    """Fetches historical sensor readings for a device."""
    table = get_table()
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('device_id').eq(device_id),
            ScanIndexForward=False, # Sort descending by timestamp
            Limit=limit
        )
        return {"data": response.get('Items', [])}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
def get_alerts(device_id: str, limit: int = 50):
    """Fetches recent sensor readings that triggered alerts (heart_rate > 120, stress > 80, fall, sound)."""
    table = get_table()
    try:
        # We fetch history and filter for alerts.
        # Alternatively, a GSI on alert status could be used, but filtering here is fine for simple queries.
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('device_id').eq(device_id),
            ScanIndexForward=False,
            Limit=limit
        )
        items = response.get('Items', [])
        
        alerts = []
        for item in items:
            is_alert = False
            if item.get('heart_rate', 0) > 120: is_alert = True
            if item.get('stress_score', 0) > 80: is_alert = True
            if item.get('fall_detected', False): is_alert = True
            if item.get('sound_alert', False): is_alert = True
            
            if is_alert:
                alerts.append(item)
                
        return {"data": alerts}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/location")
def get_location(device_id: str):
    """Fetches the latest latitude/longitude coordinates."""
    table = get_table()
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('device_id').eq(device_id),
            ScanIndexForward=False,
            Limit=1
        )
        items = response.get('Items', [])
        if not items:
            return {"message": "No location data found.", "data": None}
            
        latest = items[0]
        return {
            "data": {
                "latitude": latest.get("latitude"),
                "longitude": latest.get("longitude"),
                "timestamp": latest.get("timestamp")
            }
        }
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
