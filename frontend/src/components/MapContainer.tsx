import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polygon, useMap } from 'react-leaflet';
import L from 'leaflet';

// Bulletproof custom SVG marker icons for Leaflet in Vite
const wearerIconSvg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#EC7211" width="32" height="32">
  <circle cx="12" cy="12" r="10" fill="#FFFFFF" stroke="#EC7211" stroke-width="2"/>
  <circle cx="12" cy="12" r="4" fill="#EC7211"/>
</svg>`;

const defaultIconSvg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#00A1C9" width="24" height="24">
  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
</svg>`;

const wearerIcon = L.divIcon({
  html: wearerIconSvg,
  className: 'custom-wearer-marker',
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

const _defaultIcon = L.divIcon({
  html: defaultIconSvg,
  className: 'custom-default-marker',
  iconSize: [24, 24],
  iconAnchor: [12, 24]
});

interface GeofenceData {
  fence_id: string;
  name: string;
  type: string;
  coordinates: { lat: number; lng: number }[];
  radius_meters?: number;
  is_active: boolean;
}

interface MapContainerProps {
  latitude: number;
  longitude: number;
  geofences?: GeofenceData[];
  wearerName?: string;
}

// Component to dynamically update map center when coordinates change
const ChangeMapCenter: React.FC<{ center: [number, number] }> = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, 15);
  }, [center, map]);
  return null;
};

export const CustomMapContainer: React.FC<MapContainerProps> = ({
  latitude,
  longitude,
  geofences = [],
  wearerName = "Wearer"
}) => {
  const position: [number, number] = [latitude, longitude];

  return (
    <div className="w-full h-full relative border border-aws-slate rounded overflow-hidden select-none bg-aws-dark">
      {/* Tactical overlay indicators */}
      <div className="absolute top-3 left-12 z-[1000] bg-aws-navy/95 border border-aws-orange/30 px-3 py-1.5 rounded text-xs font-mono glow-orange flex flex-col gap-0.5">
        <span className="text-aws-gray font-bold">TACTICAL POSITION MAP</span>
        <span className="text-[10px] text-aws-orange font-semibold">Wearer: {wearerName}</span>
        <span className="text-[9px] text-aws-gray/70">Lat: {latitude.toFixed(6)}, Lng: {longitude.toFixed(6)}</span>
      </div>

      <MapContainer center={position} zoom={15} scrollWheelZoom={true} attributionControl={false}>
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          maxZoom={20}
        />
        
        {/* Active Geofence Overlays */}
        {geofences.map((fence) => {
          if (!fence.is_active) return null;
          
          if (fence.type === 'radius' && fence.coordinates.length > 0) {
            const center = fence.coordinates[0];
            return (
              <Circle
                key={fence.fence_id}
                center={[center.lat, center.lng]}
                radius={fence.radius_meters || 100}
                pathOptions={{
                  color: '#FF9900',
                  fillColor: '#FF9900',
                  fillOpacity: 0.08,
                  weight: 1.5,
                  dashArray: '5, 5'
                }}
              />
            );
          } else if (fence.type === 'polygon') {
            const polyCoords = fence.coordinates.map(pt => [pt.lat, pt.lng] as [number, number]);
            return (
              <Polygon
                key={fence.fence_id}
                positions={polyCoords}
                pathOptions={{
                  color: '#FF9900',
                  fillColor: '#FF9900',
                  fillOpacity: 0.08,
                  weight: 1.5,
                  dashArray: '5, 5'
                }}
              />
            );
          }
          return null;
        })}

        {/* Wearer marker */}
        <Marker position={position} icon={wearerIcon}>
          <Popup>
            <div className="text-xs text-aws-dark">
              <strong>{wearerName}</strong>
              <br />
              Current coordinates
            </div>
          </Popup>
        </Marker>

        {/* Map auto center */}
        <ChangeMapCenter center={position} />
      </MapContainer>
    </div>
  );
};
export default CustomMapContainer;
