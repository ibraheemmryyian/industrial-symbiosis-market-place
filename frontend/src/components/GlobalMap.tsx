import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

interface Connection {
  from_location: string;
  to_location: string;
  type: string;
}

export function GlobalMap() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConnections();
  }, []);

  async function loadConnections() {
    try {
      const { data, error } = await supabase
        .from('company_profiles')
        .select('location')
        .not('location', 'is', null);

      if (error) throw error;

      // For demonstration, we'll create sample connections
      // In a real app, this would come from actual partnership data
      const sampleConnections = data.reduce((acc: Connection[], curr, idx, arr) => {
        if (idx < arr.length - 1) {
          acc.push({
            from_location: curr.location,
            to_location: arr[idx + 1].location,
            type: idx % 2 === 0 ? 'material_exchange' : 'research_collaboration'
          });
        }
        return acc;
      }, []);

      setConnections(sampleConnections);
    } catch (error) {
      console.error('Error loading connections:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-[600px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <MapContainer center={[51.505, -0.09]} zoom={2} className="min-h-[600px]">
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {connections.map((connection, index) => (
        <Marker key={index} position={[connection.from_location.lat, connection.from_location.lng]}>
          <Popup>
            {connection.type} from {connection.from_location} to {connection.to_location}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}