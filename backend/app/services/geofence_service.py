import math

class GeofenceService:
    def is_outside_geofence(self, lat: float, lng: float, geofence: dict) -> bool:
        """Evaluate if the coordinate (lat, lng) is outside the boundaries of the geofence"""
        fence_type = geofence.get("type", "radius").lower()
        coords = geofence.get("coordinates", [])

        if fence_type == "radius":
            if not coords:
                return False
            center = coords[0]
            center_lat = center.get("lat")
            center_lng = center.get("lng")
            radius_m = geofence.get("radius_meters", 100.0)
            
            distance = self._haversine_distance(lat, lng, center_lat, center_lng)
            return distance > radius_m

        elif fence_type == "polygon":
            return not self._point_in_polygon(lat, lng, coords)

        return False

    def _haversine_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate the great-circle distance between two points in meters"""
        R = 6371000.0 # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)

        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        
        return R * c

    def _point_in_polygon(self, x: float, y: float, polygon: list[dict]) -> bool:
        """Ray-casting algorithm to determine if a point is inside a polygon"""
        num = len(polygon)
        j = num - 1
        c = False
        for i in range(num):
            pt_i = polygon[i]
            pt_j = polygon[j]
            xi, yi = pt_i.get("lat"), pt_i.get("lng")
            xj, yj = pt_j.get("lat"), pt_j.get("lng")
            
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
                c = not c
            j = i
        return c

geofence_service = GeofenceService()
