from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.core.dynamodb import db
from app.schemas.geofence import GeofenceCreate, GeofenceResponse
import uuid

router = APIRouter(prefix="/geofences", tags=["geofences"])

@router.get("/{wearer_id}", response_model=list[GeofenceResponse])
def list_geofences(wearer_id: str, current_user: dict = Depends(get_current_user)):
    """List all geofence safe zones defined for a wearer"""
    raw_fences = db.query_by_pk(f"WEARER#{wearer_id}", "GEOFENCE#")
    
    response_fences = []
    for item in raw_fences:
        # Convert coords list
        response_fences.append(GeofenceResponse(
            fence_id=item.get("fence_id"),
            wearer_id=wearer_id,
            name=item.get("name"),
            type=item.get("type"),
            coordinates=item.get("coordinates", []),
            radius_meters=item.get("radius_meters"),
            is_active=item.get("is_active", True)
        ))
    return response_fences

@router.post("", response_model=GeofenceResponse, status_code=201)
def create_geofence(payload: GeofenceCreate, current_user: dict = Depends(get_current_user)):
    """Create a new safe zone geofence (radial or polygonal)"""
    fence_id = str(uuid.uuid4())
    
    # Coordinates list to dict representation
    coords = [{"lat": pt.lat, "lng": pt.lng} for pt in payload.coordinates]

    fence_item = {
        "PK": f"WEARER#{payload.wearer_id}",
        "SK": f"GEOFENCE#{fence_id}",
        "fence_id": fence_id,
        "wearer_id": payload.wearer_id,
        "name": payload.name,
        "type": payload.type,
        "coordinates": coords,
        "radius_meters": payload.radius_meters,
        "is_active": payload.is_active
    }

    db.put_item(fence_item)

    return GeofenceResponse(
        fence_id=fence_id,
        wearer_id=payload.wearer_id,
        name=payload.name,
        type=payload.type,
        coordinates=payload.coordinates,
        radius_meters=payload.radius_meters,
        is_active=payload.is_active
    )

@router.delete("/{wearer_id}/{fence_id}")
def delete_geofence(wearer_id: str, fence_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a wearer's geofence safe zone"""
    db.delete_item(f"WEARER#{wearer_id}", f"GEOFENCE#{fence_id}")
    return {"status": "success", "message": f"Geofence {fence_id} deleted successfully"}
