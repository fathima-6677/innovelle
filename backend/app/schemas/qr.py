from pydantic import BaseModel

class QRTieredResponse(BaseModel):
    tier: int
    first_name: str
    public_message: str = "Autistic — may not respond verbally"
    emergency_contact: str | None = None
    medical_notes: str | None = None
    allergies: str | None = None
    medications: str | None = None
    last_name: str | None = None
    dob: str | None = None
    qr_tiering_rules: dict | None = None
    emergency_contacts: list | None = None
