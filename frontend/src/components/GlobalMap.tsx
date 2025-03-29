import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

interface Connection {
  from_location: { lat: number; lng: number };
  to_location: { lat: number; lng: number };
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

      // Create connections based on actual data
      const sampleConnections = data.map((profile) => ({
        from_location: { lat: 51.505, lng: -0.09 }, // Replace with actual logic
        to_location: { lat: 40.7128, lng: -74.0060 }, // Replace with actual logic
        type: 'material_exchange'
      }));

      setConnections(sampleConnections);
    } catch (error) {
      console.error('Error loading connections:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="min-h-[600px] flex items-center justify-center">Loading...</div>;
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
            {connection.type} from {connection.from_location.lat}, {connection.from_location.lng} to {connection.to_location.lat}, {connection.to_location.lng}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}