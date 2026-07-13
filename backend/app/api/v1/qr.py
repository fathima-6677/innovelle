from fastapi import APIRouter, Depends, Header, HTTPException, Request
from app.core.security import get_current_user, get_optional_user
from app.services.qr_service import qr_service
from app.schemas.qr import QRTieredResponse

router = APIRouter(tags=["qr"])

@router.post("/qr/{wearer_id}/rotate")
def rotate_qr(wearer_id: str, current_user: dict = Depends(get_current_user)):
    """Generate or rotate dynamic 24h KMS-signed QR token for wearer"""
    token = qr_service.generate_qr_token(wearer_id)
    return {
        "qr_payload": token,
        "expires_in_hours": 24
    }

# Public resolution endpoint - no global BearerAuth guard, rate-limited via WAF
@router.get("/qr/resolve/{token}", response_model=QRTieredResponse)
def resolve_qr(token: str, request: Request):
    """Public/Authenticated endpoint to resolve tiered wearer details from scanned QR token"""
    user = get_optional_user(request)
    role = "public"
    if user:
        role = user.get("custom:role") or (user.get("cognito:groups", ["caregiver"])[0] if user.get("cognito:groups") else "caregiver")
    return qr_service.resolve_qr_token(token, scanner_role=role)
