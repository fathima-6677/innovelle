from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.core.dynamodb import db
from app.schemas.alerts import AlertItem
from app.services.notification_service import notification_service
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
    all_alerts = db.query_gsi1(f"WEARER#{wearer_id}", "ALERT#")
    
    target_alert = None
    for item in all_alerts:
        if item.get("alert_id") == alert_id:
            target_alert = item
            break
            
    if not target_alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    target_alert["ack_status"] = "acknowledged"
    target_alert["ack_by"] = current_user.get("email", "caregiver@autiguard.org")
    target_alert["ack_at"] = datetime.datetime.utcnow().isoformat()
    db.put_item(target_alert)

    org_id = current_user.get("org_id", "ORG#demo-org-99")
    from app.main import ws_manager
    await ws_manager.broadcast_to_org(org_id, {
        "wearer_id": wearer_id,
        "type": "alert"
    })

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


# ── Panic Button ──────────────────────────────────────────────────────────────

@router.post("/panic/{wearer_id}", status_code=status.HTTP_201_CREATED)
async def trigger_panic_alert(wearer_id: str, current_user: dict = Depends(get_current_user)):
    """Manually trigger an SOS panic alert for a wearer.
    Creates the alert, broadcasts via WebSocket, and notifies emergency contacts via SMS."""
    now_str = datetime.datetime.utcnow().isoformat()
    alert_id = f"alert-panic-{int(datetime.datetime.utcnow().timestamp())}"
    org_id = current_user.get("org_id", "ORG#demo-org-99")

    wearer_profile = db.get_item(f"WEARER#{wearer_id}", "PROFILE")
    wearer_name = (
        f"{wearer_profile.get('first_name', 'Wearer')} {wearer_profile.get('last_name', '')}".strip()
        if wearer_profile else "Wearer"
    )
    contacts = wearer_profile.get("emergency_contacts", []) if wearer_profile else []

    alert_item = {
        "PK": f"WEARER#{wearer_id}",
        "SK": f"ALERT#{now_str}",
        "GSI1PK": f"WEARER#{wearer_id}",
        "GSI1SK": f"ALERT#panic#{now_str}",
        "alert_id": alert_id,
        "wearer_id": wearer_id,
        "wearer_name": wearer_name,
        "type": "panic_button",
        "severity": "critical",
        "details": {
            "triggered_by": current_user.get("email", "caregiver@autiguard.org"),
            "message": f"SOS panic button manually triggered for {wearer_name}"
        },
        "ack_status": "unacknowledged",
        "timestamp": now_str
    }
    db.put_item(alert_item)

    from app.main import ws_manager
    await ws_manager.broadcast_to_org(org_id, {
        "wearer_id": wearer_id,
        "type": "alert",
        "alert_type": "panic_button"
    })

    for contact in contacts:
        phone = contact.get("phone")
        if phone:
            notification_service.send_sms(
                phone,
                f"SOS PANIC: Emergency alert triggered for {wearer_name}. Please respond immediately."
            )

    return {
        "status": "created",
        "alert_id": alert_id,
        "message": f"Panic alert created and emergency contacts notified."
    }
