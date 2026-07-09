from fastapi import APIRouter, Depends, Header, HTTPException
from app.core.security import get_current_user
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
def resolve_qr(token: str, x_scanner_role: str | None = Header(default="public")):
    """Public unauthenticated endpoint to resolve tiered wearer details from scanned QR token"""
    # Accept scanner role via custom header or evaluate from token context
    return qr_service.resolve_qr_token(token, scanner_role=x_scanner_role)
