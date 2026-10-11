import React, { useRef, useMemo, useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, LayersControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { API_BASE_URL } from '../config/api';

const { BaseLayer } = LayersControl;

const markerIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

function DraggableMarker({ 
  zone, 
  onSnap, 
  onRename, 
  onDelete 
}: { 
  zone: any, 
  onSnap: (idx: number, lat: number, lon: number, street: string) => void,
  onRename: (idx: number, newName: string) => void,
  onDelete: (idx: number) => void
}) {
  const [position, setPosition] = useState({ lat: zone.lat, lng: zone.lon });
  const [street, setStreet] = useState(zone.street || 'Ubicación actual');
  const markerRef = useRef<any>(null);

  const eventHandlers = useMemo(
    () => ({
      dragend() {
        const marker = markerRef.current;
        if (marker != null) {
          const newPos = marker.getLatLng();
          // Call snap API
          fetch(`${API_BASE_URL}/api/snap`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat: newPos.lat, lon: newPos.lng })
          })
          .then(res => res.json())
          .then(data => {
            if (data.status === 'success') {
              setPosition({ lat: data.lat, lng: data.lon });
              setStreet(data.street);
              onSnap(zone.idx, data.lat, data.lon, data.street);
            } else {
              setPosition(newPos);
            }
          })
          .catch(() => setPosition(newPos));
        }
      },
    }),
    [zone.idx, onSnap]
  );

  useEffect(() => {
    setPosition({ lat: zone.lat, lng: zone.lon });
  }, [zone.lat, zone.lon]);

  return (
    <Marker draggable={true} eventHandlers={eventHandlers} position={position} ref={markerRef} icon={markerIcon}>
      <Popup minWidth={160}>
        <div style={{fontWeight: 'bold', fontSize: '14px', color: '#ea580c'}}>{zone.name}</div>
        <div style={{fontSize: '12px', marginTop: '4px', marginBottom: '8px'}}>
          <b>Vía:</b> {street}<br/>
          <b>Coord:</b> {position.lat.toFixed(6)}, {position.lng.toFixed(6)}
        </div>
        <div style={{display: 'flex', gap: '6px', borderTop: '1px solid #e2e8f0', paddingTop: '6px'}}>
          <button 
            type="button"
            onClick={() => {
              const newName = prompt('Modificar nombre de la zona:', zone.name);
              if (newName && newName.trim() !== '') {
                onRename(zone.idx, newName.trim());
              }
            }}
            style={{background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '4px', padding: '4px 8px', fontSize: '11px', cursor: 'pointer', fontWeight: 600}}
          >
            ✏️ Renombrar
          </button>
          <button 
            type="button"
            onClick={() => {
              if (confirm(`¿Eliminar la zona "${zone.name}"?`)) {
                onDelete(zone.idx);
              }
            }}
            style={{background: '#fee2e2', border: '1px solid #fca5a5', color: '#b91c1c', borderRadius: '4px', padding: '4px 8px', fontSize: '11px', cursor: 'pointer', fontWeight: 600}}
          >
            🗑️ Eliminar
          </button>
        </div>
      </Popup>
    </Marker>
  );
}

export default function CalibracionMap({ 
  zones, 
  onSnap, 
  onRename, 
  onDelete 
}: { 
  zones: any[], 
  onSnap: (idx: number, lat: number, lon: number, street: string) => void,
  onRename: (idx: number, newName: string) => void,
  onDelete: (idx: number) => void
}) {
  const center: [number, number] = [8.74798, -75.88143];

  return (
    <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%', zIndex: 1 }}>
      <LayersControl position="topright">
        <BaseLayer checked name="Mapa de Calles">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
        </BaseLayer>
        <BaseLayer name="Vista Satelital (Esri)">
          <TileLayer
            attribution='Tiles &copy; Esri &mdash; Source: Esri'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          />
        </BaseLayer>
      </LayersControl>
      
      {zones.map((zone) => (
        <DraggableMarker 
          key={zone.idx} 
          zone={zone} 
          onSnap={onSnap} 
          onRename={onRename} 
          onDelete={onDelete} 
        />
      ))}
    </MapContainer>
  );
}
