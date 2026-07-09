import jwt
import datetime
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import decrypt_field
from app.core.dynamodb import db

class QRService:
    def generate_qr_token(self, wearer_id: str) -> str:
        """Generate a signed JWT token with a 24-hour TTL for QR scanning"""
        # For security, we sign with a simple local secret or KMS asymmetric key
        # In a real environment, we'd use KMS sign API. For simplicity and portability,
        # we sign using HS256 with a key managed in AWS Secrets Manager or settings.
        payload = {
            "sub": wearer_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            "iat": datetime.datetime.utcnow(),
            "iss": "autiguard-backend"
        }
        # In local/mock mode or regular JWT signature
        secret_key = settings.KMS_KEY_ID if settings.KMS_KEY_ID != "mockKmsKeyId" else "localSecretKey"
        return jwt.encode(payload, secret_key, algorithm="HS256")

    def resolve_qr_token(self, token: str, scanner_role: str = "public") -> dict:
        """Resolve ephemeral QR token and apply tiered data disclosure rules"""
        secret_key = settings.KMS_KEY_ID if settings.KMS_KEY_ID != "mockKmsKeyId" else "localSecretKey"
        try:
            decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
            wearer_id = decoded["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="QR code expired. Please request the caregiver to refresh the QR image."
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid QR token payload."
            )

        # Retrieve wearer profile from DynamoDB
        wearer_profile = db.get_item(f"WEARER#{wearer_id}", "PROFILE")
        if not wearer_profile:
            raise HTTPException(status_code=404, detail="Wearer profile not found")

        # Determine Tier level based on scanner's authenticated role / header
        # public -> Tier 1
        # responder -> Tier 2
        # caregiver / admin -> Tier 3
        tier = 1
        if scanner_role in ["responder", "medical"]:
            tier = 2
        elif scanner_role in ["caregiver", "org_admin", "super_admin"]:
            tier = 3

        # Formulate response depending on Tier
        response = {
            "tier": tier,
            "first_name": wearer_profile.get("first_name"),
            "public_message": "Autistic — may not respond verbally",
            "emergency_contact": wearer_profile.get("emergency_contacts", [{}])[0].get("phone") if wearer_profile.get("emergency_contacts") else None,
        }

        if tier >= 2:
            # Decrypt medical fields
            response["medical_notes"] = decrypt_field(wearer_profile.get("medical_notes", ""))
            response["allergies"] = decrypt_field(wearer_profile.get("allergies", ""))
            response["medications"] = decrypt_field(wearer_profile.get("medications", ""))

        if tier == 3:
            response["last_name"] = wearer_profile.get("last_name")
            response["dob"] = wearer_profile.get("dob")
            response["qr_tiering_rules"] = wearer_profile.get("qr_tiering_rules", {})
            response["emergency_contacts"] = wearer_profile.get("emergency_contacts", [])

        # Log this scan in DynamoDB
        scan_log = {
            "PK": f"WEARER#{wearer_id}",
            "SK": f"QRSCAN#{datetime.datetime.utcnow().isoformat()}",
            "scan_id": f"scan-{datetime.datetime.utcnow().timestamp()}",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "tier_resolved": tier,
            "scanner_role": scanner_role
        }
        db.put_item(scan_log)

        # Trigger notification log / real-time alert for caregivers
        self._trigger_caregiver_notification(wearer_id, tier)

        return response

    def _trigger_caregiver_notification(self, wearer_id: str, tier: int):
        # Create an warning alert that the wearer's QR code was scanned
        alert = {
            "PK": f"WEARER#{wearer_id}",
            "SK": f"ALERT#{datetime.datetime.utcnow().isoformat()}",
            "GSI1PK": f"WEARER#{wearer_id}",
            "GSI1SK": f"ALERT#qr_scan#{datetime.datetime.utcnow().isoformat()}",
            "alert_id": f"alert-qr-{datetime.datetime.utcnow().timestamp()}",
            "wearer_id": wearer_id,
            "wearer_name": "Wearer", # Will resolve dynamically or fetch on query
            "type": "qr_scan",
            "severity": "info" if tier == 3 else "warning",
            "details": {
                "message": f"QR identity card scanned (Resolved Tier {tier})",
                "timestamp": datetime.datetime.utcnow().isoformat()
            },
            "ack_status": "unacknowledged",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        db.put_item(alert)

qr_service = QRService()
