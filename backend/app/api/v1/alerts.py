from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.core.dynamodb import db
from app.schemas.alerts import AlertItem
import datetime

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("", response_model=list[AlertItem])
def list_alerts(current_user: dict = Depends(get_current_user)):
    """List all alerts across all wearers in the organization"""
    org_id = current_user.get("org_id", "ORG#demo-org-99")
    
    # 1. Fetch all wearers in the org
    wearer_linkages = db.query_by_pk(org_id, "WEARER#")
    
    alerts = []
    for link in wearer_linkages:
        wearer_id = link.get("SK").replace("WEARER#", "")
        # Query GSI1 to fetch all alerts for this wearer
        wearer_alerts = db.query_gsi1(f"WEARER#{wearer_id}", "ALERT#")
        for wa in wearer_alerts:
            alerts.append(AlertItem(
                alert_id=wa.get("alert_id"),
                wearer_id=wa.get("wearer_id"),
                wearer_name=wa.get("wearer_name", "Wearer"),
                type=wa.get("type"),
                severity=wa.get("severity"),
                details=wa.get("details", {}),
                ack_status=wa.get("ack_status"),
                timestamp=datetime.datetime.fromisoformat(wa.get("timestamp")),
                ack_by=wa.get("ack_by"),
                ack_at=datetime.datetime.fromisoformat(wa.get("ack_at")) if wa.get("ack_at") else None
            ))
            
    # Sort alerts chronologically (newest first)
    alerts.sort(key=lambda x: x.timestamp, reverse=True)
    return alerts

@router.post("/{wearer_id}/acknowledge/{alert_id}")
async def acknowledge_alert(wearer_id: str, alert_id: str, current_user: dict = Depends(get_current_user)):
    """Acknowledge an active critical/warning alert"""
    # Alerts are stored under WEARER#<id> with SK ALERT#<timestamp>
    # Since we don't have the exact timestamp in the path, we must find it
    # We query GSI1 which uses GSI1PK = WEARER#<id> and GSI1SK begins with ALERT#
    all_alerts = db.query_gsi1(f"WEARER#{wearer_id}", "ALERT#")
    
    target_alert = None
    for item in all_alerts:
        if item.get("alert_id") == alert_id:
            target_alert = item
            break
            
    if not target_alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Update alert properties
    target_alert["ack_status"] = "acknowledged"
    target_alert["ack_by"] = current_user.get("email", "caregiver@autiguard.org")
    target_alert["ack_at"] = datetime.datetime.utcnow().isoformat()
    
    # Save back to table
    db.put_item(target_alert)

    # Broadcast alert acknowledgement update
    org_id = current_user.get("org_id", "ORG#demo-org-99")
    from app.main import ws_manager
    await ws_manager.broadcast_to_org(org_id, {
        "wearer_id": wearer_id,
        "type": "alert"
    })

    # Insert administrative Audit Log
    audit_id = f"audit-{int(datetime.datetime.utcnow().timestamp())}"
    audit_log = {
        "PK": current_user.get("org_id", "ORG#demo-org-99"),
        "SK": f"AUDIT#{datetime.datetime.utcnow().isoformat()}#{audit_id}",
        "action": "acknowledge_alert",
        "performed_by": current_user.get("email", "caregiver@autiguard.org"),
        "details": {
            "alert_id": alert_id,
            "wearer_id": wearer_id,
            "message": f"Acknowledged alert of type {target_alert.get('type')}"
        },
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    db.put_item(audit_log)

    return {"status": "success", "message": "Alert successfully acknowledged"}
