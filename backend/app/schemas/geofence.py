from pydantic import BaseModel

class GeofenceCoord(BaseModel):
    lat: float
    lng: float

class GeofenceCreate(BaseModel):
    wearer_id: str
    name: str
    type: str  # radius, polygon
    coordinates: list[GeofenceCoord]
    radius_meters: float | None = None
    is_active: bool = True

class GeofenceResponse(BaseModel):
    fence_id: str
    wearer_id: str
    name: str
    type: str
    coordinates: list[GeofenceCoord]
    radius_meters: float | None = None
    is_active: bool
