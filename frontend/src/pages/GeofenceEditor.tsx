import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import { useAuthStore } from '../store/authStore';
import { Map, Plus, Trash2, Shield } from 'lucide-react';
import { CustomMapContainer } from '../components/MapContainer';
import { API_BASE_URL } from '../config';

export const GeofenceEditor: React.FC = () => {
  const { token } = useAuthStore();
  const [selectedWearerId, setSelectedWearerId] = useState<string>('');
  const [wearersList, setWearersList] = useState<any[]>([]);

  // Geofence states
  const [geofences, setGeofences] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [radiusMeters, setRadiusMeters] = useState(100);
  const [centerLat, setCenterLat] = useState(11.9416);
  const [centerLng, setCenterLng] = useState(79.8083);

  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const fetchWearers = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/wearers`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setWearersList(data);
        if (data.length > 0 && !selectedWearerId) {
          setSelectedWearerId(data[0].wearer_id);
        }
      }
    } catch {
      const mock = [{ wearer_id: 'wearer-99', first_name: 'Aarav', last_name: 'Sharma' }];
      setWearersList(mock);
      setSelectedWearerId(mock[0].wearer_id);
    }
  }, [token, selectedWearerId]);

  const fetchGeofences = useCallback(async () => {
    if (!selectedWearerId) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/geofences/${selectedWearerId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setGeofences(data);
      }
    } catch {
      // offline mock
      setGeofences([
        {
          fence_id: 'fence-1',
          name: 'Home Safe Area',
          type: 'radius',
          coordinates: [{ lat: 11.9416, lng: 79.8083 }],
          radius_meters: 150,
          is_active: true
        }
      ]);
    }
  }, [selectedWearerId, token]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    const payload = {
      wearer_id: selectedWearerId,
      name,
      type: 'radius',
      coordinates: [{ lat: centerLat, lng: centerLng }],
      radius_meters: radiusMeters,
      is_active: true
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/geofences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setMessage('Geofence boundary successfully saved. AWS Lambda geofence engine updated.');
        setName('');
        fetchGeofences();
      }
    } catch {
      // offline simulation add
      const newFence = {
        fence_id: `fence-${Date.now()}`,
        name,
        type: 'radius',
        coordinates: [{ lat: centerLat, lng: centerLng }],
        radius_meters: radiusMeters,
        is_active: true
      };
      setGeofences(prev => [...prev, newFence]);
      setName('');
      setMessage('Offline simulation: Geofence cached locally.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (fenceId: string) => {
    // optimistic delete
    setGeofences(prev => prev.filter(f => f.fence_id !== fenceId));

    try {
      await fetch(`${API_BASE_URL}/api/v1/geofences/${selectedWearerId}/${fenceId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
    } catch {
      console.log("Could not delete on server, offline fallback updated.");
    }
  };

  useEffect(() => {
    fetchWearers();
  }, [fetchWearers]);

  useEffect(() => {
    fetchGeofences();
  }, [fetchGeofences]);

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Navbar />

      <main className="flex-1 overflow-y-auto p-6 bg-aws-dark select-none">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold text-black flex items-center gap-2">
              <Map className="text-aws-orange" size={24} />
              GEOFENCE BOUNDARY CONFIGURATIONS
            </h1>
            <p className="text-xs text-black/70 mt-1 uppercase font-mono">Lambda Stream Boundary Evaluators</p>
          </div>

          <select
            value={selectedWearerId}
            onChange={(e) => setSelectedWearerId(e.target.value)}
            className="bg-aws-navy border border-aws-slate rounded text-sm text-black px-3 py-1.5 focus:outline-none focus:border-aws-orange font-mono"
          >
            {wearersList.map(w => (
              <option key={w.wearer_id} value={w.wearer_id}>
                {w.first_name} {w.last_name}
              </option>
            ))}
          </select>
        </div>

        {message && (
          <div className="mb-6 p-4 rounded bg-aws-teal/10 border border-aws-teal/30 text-aws-teal text-xs font-mono text-center">
            {message}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[500px]">
          {/* Geofence Form & List */}
          <div className="lg:col-span-4 flex flex-col gap-6 h-full overflow-y-auto">
            {/* Create Geofence */}
            <form onSubmit={handleCreate} className="glass-panel p-5 rounded-lg space-y-4">
              <h2 className="text-xs font-bold text-black uppercase tracking-wider border-b border-aws-slate pb-2 flex items-center gap-1.5">
                <Plus size={16} className="text-aws-orange" /> Add Safe Zone
              </h2>

              <div>
                <label className="block text-[10px] font-mono text-black/70 uppercase mb-1">Zone Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-xs text-black focus:outline-none focus:border-aws-orange"
                  placeholder="e.g. Home, School, Park"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-mono text-black/70 uppercase mb-1">Lat Center</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={centerLat}
                    onChange={(e) => setCenterLat(parseFloat(e.target.value))}
                    className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-xs text-black focus:outline-none focus:border-aws-orange font-mono"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-mono text-black/70 uppercase mb-1">Lng Center</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={centerLng}
                    onChange={(e) => setCenterLng(parseFloat(e.target.value))}
                    className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-xs text-black focus:outline-none focus:border-aws-orange font-mono"
                    required
                  />
                </div>
              </div>

              <button
                type="button"
                onClick={() => {
                  if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                      (position) => {
                        setCenterLat(parseFloat(position.coords.latitude.toFixed(4)));
                        setCenterLng(parseFloat(position.coords.longitude.toFixed(4)));
                        setMessage("GPS location retrieved successfully.");
                      },
                      (error) => {
                        setMessage(`GPS retrieval failed: ${error.message}`);
                      }
                    );
                  } else {
                    setMessage("Geolocation is not supported by this browser.");
                  }
                }}
                className="w-full py-1.5 bg-aws-navy border border-aws-slate hover:bg-aws-navy/80 text-black font-semibold text-[10px] rounded transition-all flex items-center justify-center gap-1"
              >
                <Map size={12} className="text-aws-orange" /> Use Current GPS Location
              </button>

              <div>
                <label className="block text-[10px] font-mono text-black/70 uppercase mb-1">Radius (Meters)</label>
                <input
                  type="number"
                  value={radiusMeters}
                  onChange={(e) => setRadiusMeters(parseInt(e.target.value))}
                  className="w-full px-3 py-2 bg-aws-navy border border-aws-slate rounded text-xs text-black focus:outline-none focus:border-aws-orange font-mono"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={saving}
                className="w-full py-2 bg-aws-orange hover:bg-aws-orange/90 text-black font-bold text-xs rounded transition-all"
              >
                {saving ? 'Registering boundaries...' : 'Create Safe Boundary'}
              </button>
            </form>

            {/* List Active Geofences */}
            <div className="glass-panel p-5 rounded-lg flex-1 overflow-y-auto">
              <h2 className="text-xs font-bold text-black uppercase tracking-wider border-b border-aws-slate pb-2 mb-3">
                Active Boundaries
              </h2>
              
              <div className="space-y-2">
                {geofences.map(fence => (
                  <div key={fence.fence_id} className="flex items-center justify-between p-3 bg-aws-navy rounded border border-aws-slate">
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-black flex items-center gap-1">
                        <Shield size={12} className="text-aws-teal" /> {fence.name}
                      </span>
                      <span className="text-[10px] text-black/60 font-mono mt-0.5">
                        Rad: {fence.radius_meters}m | center: {fence.coordinates?.[0]?.lat.toFixed(4)}, {fence.coordinates?.[0]?.lng.toFixed(4)}
                      </span>
                    </div>

                    <button
                      onClick={() => handleDelete(fence.fence_id)}
                      className="p-1.5 hover:bg-red-600/10 border border-transparent hover:border-red-500/20 text-red-400 rounded transition-all"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Map display */}
          <div className="lg:col-span-8 h-full">
            <CustomMapContainer
              latitude={centerLat}
              longitude={centerLng}
              geofences={geofences}
              wearerName="Target Center"
            />
          </div>
        </div>
      </main>
    </div>
  );
};
export default GeofenceEditor;
