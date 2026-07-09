from pydantic import BaseModel
from datetime import datetime

class AlertItem(BaseModel):
    alert_id: str
    wearer_id: str
    wearer_name: str
    type: str  # fall, geofence_breach, audio_distress, panic_button, low_battery
    severity: str  # critical, warning, info
    details: dict
    ack_status: str  # acknowledged, unacknowledged, escalated
    timestamp: datetime
    ack_by: str | None = None
    ack_at: datetime | None = None
