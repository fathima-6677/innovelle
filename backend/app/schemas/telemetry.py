from pydantic import BaseModel
from datetime import datetime

class TelemetryItem(BaseModel):
    timestamp: datetime
    heart_rate: float
    latitude: float
    longitude: float
    accel_x: float
    accel_y: float
    accel_z: float
    accel_magnitude: float
    stress_index: float
    risk_level: str
    battery_level: float
    connectivity_status: str

class TelemetryBatch(BaseModel):
    wearer_id: str
    readings: list[TelemetryItem]
