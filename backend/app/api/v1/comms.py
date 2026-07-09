from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.dynamodb import db
from app.schemas.comms import CommLogCreate, CommLogResponse
import uuid
import datetime

router = APIRouter(prefix="/comms", tags=["comms"])

@router.post("", response_model=CommLogResponse, status_code=201)
def create_comm_log(payload: CommLogCreate, current_user: dict = Depends(get_current_user)):
    """Log non-verbal communication request triggered from wearer's device"""
    event_id = str(uuid.uuid4())
    now_str = datetime.datetime.utcnow().isoformat()

    log_item = {
        "PK": f"WEARER#{payload.wearer_id}",
        "SK": f"COMMLOG#{now_str}",
        "event_id": event_id,
        "wearer_id": payload.wearer_id,
        "category_code": payload.category_code,
        "timestamp": now_str
    }

    db.put_item(log_item)

    return CommLogResponse(
        event_id=event_id,
        wearer_id=payload.wearer_id,
        category_code=payload.category_code,
        timestamp=datetime.datetime.fromisoformat(now_str)
    )

@router.get("/{wearer_id}", response_model=list[CommLogResponse])
def get_comm_logs(wearer_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieve all communication events logged for wearer"""
    raw_logs = db.query_by_pk(f"WEARER#{wearer_id}", "COMMLOG#")
    
    logs = []
    for item in raw_logs:
        logs.append(CommLogResponse(
            event_id=item.get("event_id"),
            wearer_id=wearer_id,
            category_code=item.get("category_code"),
            timestamp=datetime.datetime.fromisoformat(item.get("SK").replace("COMMLOG#", ""))
        ))
        
    # Sort chronologically (newest first)
    logs.sort(key=lambda x: x.timestamp, reverse=True)
    return logs
