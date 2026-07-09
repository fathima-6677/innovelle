from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user, encrypt_field, decrypt_field
from app.core.dynamodb import db
from app.schemas.wearers import WearerCreate, WearerProfile
import uuid
import datetime

router = APIRouter(prefix="/wearers", tags=["wearers"])

@router.get("", response_model=list[WearerProfile])
def list_wearers(current_user: dict = Depends(get_current_user)):
    """List all wearers inside the caregiver's organization"""
    org_id = current_user.get("org_id", "ORG#demo-org-99")
    items = db.query_by_pk(org_id, "WEARER#")
    
    wearers = []
    for item in items:
        # Each item represents a wearer associated with ORG
        # Retrieve wearer profile
        wearer_id = item.get("SK").replace("WEARER#", "")
        profile = db.get_item(f"WEARER#{wearer_id}", "PROFILE")
        if profile:
            # Decrypt fields for rendering
            profile["medical_notes"] = decrypt_field(profile.get("medical_notes", ""))
            profile["allergies"] = decrypt_field(profile.get("allergies", ""))
            profile["medications"] = decrypt_field(profile.get("medications", ""))
            wearers.append(profile)
    return wearers

@router.post("", response_model=WearerProfile, status_code=201)
def create_wearer(payload: WearerCreate, current_user: dict = Depends(get_current_user)):
    """Create a new wearer profile with PII envelope encryption"""
    org_id = current_user.get("org_id", "ORG#demo-org-99")
    wearer_id = str(uuid.uuid4())
    
    # Encrypt PII fields
    encrypted_notes = encrypt_field(payload.medical_notes or "")
    encrypted_allergies = encrypt_field(payload.allergies or "")
    encrypted_medications = encrypt_field(payload.medications or "")

    now = datetime.datetime.utcnow().isoformat()
    wearer_item = {
        "PK": f"WEARER#{wearer_id}",
        "SK": "PROFILE",
        "wearer_id": wearer_id,
        "org_id": org_id,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "dob": payload.dob.isoformat(),
        "medical_notes": encrypted_notes,
        "allergies": encrypted_allergies,
        "medications": encrypted_medications,
        "qr_tiering_rules": payload.qr_tiering_rules,
        "emergency_contacts": payload.emergency_contacts,
        "created_at": now
    }

    # Put Wearer Profile
    db.put_item(wearer_item)

    # Put Org to Wearer linkage (so we can query wearers in an org)
    linkage_item = {
        "PK": org_id,
        "SK": f"WEARER#{wearer_id}",
        "wearer_id": wearer_id,
        "created_at": now
    }
    db.put_item(linkage_item)

    # Return profile with plaintext fields
    return WearerProfile(
        wearer_id=wearer_id,
        org_id=org_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        dob=payload.dob.isoformat(),
        medical_notes=payload.medical_notes,
        allergies=payload.allergies,
        medications=payload.medications,
        qr_tiering_rules=payload.qr_tiering_rules,
        emergency_contacts=payload.emergency_contacts,
        created_at=now
    )

@router.get("/{id}", response_model=WearerProfile)
def get_wearer(id: str, current_user: dict = Depends(get_current_user)):
    """Retrieve wearer profile by ID"""
    profile = db.get_item(f"WEARER#{id}", "PROFILE")
    if not profile:
        raise HTTPException(status_code=404, detail="Wearer profile not found")

    profile["medical_notes"] = decrypt_field(profile.get("medical_notes", ""))
    profile["allergies"] = decrypt_field(profile.get("allergies", ""))
    profile["medications"] = decrypt_field(profile.get("medications", ""))
    return profile

@router.put("/{id}", response_model=WearerProfile)
def update_wearer(id: str, payload: WearerCreate, current_user: dict = Depends(get_current_user)):
    """Update wearer profile details"""
    profile = db.get_item(f"WEARER#{id}", "PROFILE")
    if not profile:
        raise HTTPException(status_code=404, detail="Wearer profile not found")

    encrypted_notes = encrypt_field(payload.medical_notes or "")
    encrypted_allergies = encrypt_field(payload.allergies or "")
    encrypted_medications = encrypt_field(payload.medications or "")

    profile.update({
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "dob": payload.dob.isoformat(),
        "medical_notes": encrypted_notes,
        "allergies": encrypted_allergies,
        "medications": encrypted_medications,
        "qr_tiering_rules": payload.qr_tiering_rules,
        "emergency_contacts": payload.emergency_contacts,
    })

    db.put_item(profile)

    return WearerProfile(
        wearer_id=id,
        org_id=profile.get("org_id"),
        first_name=payload.first_name,
        last_name=payload.last_name,
        dob=payload.dob.isoformat(),
        medical_notes=payload.medical_notes,
        allergies=payload.allergies,
        medications=payload.medications,
        qr_tiering_rules=payload.qr_tiering_rules,
        emergency_contacts=payload.emergency_contacts,
        created_at=profile.get("created_at")
    )

@router.delete("/{id}")
def delete_wearer(id: str, current_user: dict = Depends(get_current_user)):
    """Delete wearer profile"""
    org_id = current_user.get("org_id", "ORG#demo-org-99")
    db.delete_item(f"WEARER#{id}", "PROFILE")
    db.delete_item(org_id, f"WEARER#{id}")
    return {"status": "success", "message": f"Wearer {id} deleted successfully"}
