"use client";

import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Ícono por defecto
const iconUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png';
const shadowUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png';
const DefaultIcon = L.icon({
  iconUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Ícono personalizado rojo para las Ambulancias
const AmbulanceIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

export default function Map({ results }: { results: any }) {
  const position: [number, number] = [8.74798, -75.88143];

  return (
    <MapContainer 
      center={position} 
      zoom={13} 
      style={{ height: '100%', width: '100%', zIndex: 1 }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {/* Nodos de Demanda (Zonas de Emergencia Simuladas) */}
      {results && results.node_coords && results.node_coords.map((coord: [number, number], idx: number) => (
        <CircleMarker key={`node-${idx}`} center={coord} radius={6} color="#3b82f6" fillColor="#3b82f6" fillOpacity={0.4}>
          <Popup><b>Zona de Demanda {idx + 1}</b></Popup>
        </CircleMarker>
      ))}

      {/* Bases Asignadas (Ambulancias) */}
      {results && results.base_coords && results.base_coords.map((coord: [number, number], idx: number) => {
        const asignadas = results.allocation[`${idx}`] || results.allocation[idx] || 0;
        if (asignadas > 0) {
          return (
            <Marker key={`base-${idx}`} position={coord} icon={AmbulanceIcon}>
              <Popup>
                <div style={{ textAlign: 'center' }}>
                  <b style={{ color: '#ef4444' }}>🚑 Base Estratégica {idx + 1}</b><br/>
                  Ambulancias en posición: <b>{asignadas}</b>
                </div>
              </Popup>
            </Marker>
          );
        }
        return null;
      })}

      {!results && (
        <Marker position={position}>
          <Popup>Centro de Montería<br/>(Ajusta los parámetros y presiona Ejecutar)</Popup>
        </Marker>
      )}
    </MapContainer>
  );
}
