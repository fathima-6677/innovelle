from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Any

class WearerCreate(BaseModel):
    first_name: str
    last_name: str
    dob: date
    medical_notes: str | None = None
    allergies: str | None = None
    medications: str | None = None
    qr_tiering_rules: dict[str, Any] = Field(default_factory=dict)
    emergency_contacts: list[dict[str, str]] = Field(default_factory=list)

class WearerProfile(BaseModel):
    wearer_id: str
    org_id: str
    first_name: str
    last_name: str
    dob: str
    medical_notes: str | None = None
    allergies: str | None = None
    medications: str | None = None
    qr_tiering_rules: dict[str, Any] = {}
    emergency_contacts: list[dict[str, str]] = []
    created_at: datetime
