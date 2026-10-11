"use client";

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, Tooltip, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Ícono predeterminado para evitar errores de Leaflet en Next.js
const iconUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png';
const shadowUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png';
L.Marker.prototype.options.icon = L.icon({
  iconUrl, shadowUrl, iconSize: [25, 41], iconAnchor: [12, 41]
});

// Íconos personalizados usando HTML (divIcon) compactos y diferenciados
// Hospitales: CUADRADO AZUL con letra H
const createHospitalIcon = () => L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color: #1d4ed8; color: #ffffff; width: 21px; height: 21px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-family: system-ui, -apple-system, sans-serif; font-size: 11px; border: 1.5px solid #ffffff; box-shadow: 0 2px 5px rgba(29, 78, 216, 0.4);">H</div>`,
  iconSize: [21, 21],
  iconAnchor: [10.5, 10.5]
});

// Bases Tácticas en Vía: CÍRCULO VERDE ESMERALDA con letra B (Diferenciación total de forma y color)
const createTacticalBaseIcon = () => L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color: #059669; color: #ffffff; width: 21px; height: 21px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-family: system-ui, -apple-system, sans-serif; font-size: 11px; border: 1.5px solid #ffffff; box-shadow: 0 2px 5px rgba(5, 150, 105, 0.45);">B</div>`,
  iconSize: [21, 21],
  iconAnchor: [10.5, 10.5]
});

// Unidades (Ambulancias): Compactas y nítidas
const createAmbulanceIcon = (label: string, isMoving: boolean = false) => L.divIcon({
  className: 'custom-div-icon',
  html: isMoving 
    ? `<div style="background-color: #2563eb; color: #ffffff; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; border: 2px solid #ffffff; box-shadow: 0 0 12px rgba(37,99,235,0.85); font-size: 0.72rem; transform: scale(1.1); transition: transform 0.2s;">${label}</div>`
    : `<div style="background-color: #dc2626; color: #ffffff; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; border: 1.5px solid #ffffff; box-shadow: 0 2px 5px rgba(0,0,0,0.25); font-size: 0.68rem;">${label}</div>`,
  iconSize: isMoving ? [26, 26] : [22, 22],
  iconAnchor: isMoving ? [13, 13] : [11, 11]
});

// Controlador de cámara automática para múltiples rutas concurrentes
function MapCameraController({ 
  activeRoutesMap,
  focusedIncidentId,
  resetTrigger,
  fitAllTrigger,
  focusRouteTrigger
}: { 
  activeRoutesMap: Record<number, any>; 
  focusedIncidentId?: number | null;
  resetTrigger?: number; 
  fitAllTrigger?: number;
  focusRouteTrigger?: number;
}) {
  const map = useMap();

  // 1. Auto-enfoque cuando cambia el incidente enfocado o se dispara re-enfoque
  useEffect(() => {
    let targetRoute = focusedIncidentId ? activeRoutesMap[focusedIncidentId] : null;
    if (!targetRoute) {
      const activeList = Object.values(activeRoutesMap);
      if (activeList.length > 0) {
        targetRoute = activeList[activeList.length - 1];
      }
    }

    if (targetRoute?.primary && targetRoute.primary.length > 0) {
      const bounds = L.latLngBounds(targetRoute.primary);
      map.fitBounds(bounds, {
        paddingTopLeft: [70, 70],
        paddingBottomRight: [70, 70],
        maxZoom: 16,
        animate: true,
        duration: 1.2
      });
    }
  }, [focusedIncidentId, focusRouteTrigger, map, activeRoutesMap]);

  // 2. Encuadrar TODAS las emergencias activas simultáneamente en la pantalla
  useEffect(() => {
    if (fitAllTrigger && fitAllTrigger > 0) {
      const allCoords: [number, number][] = [];
      Object.values(activeRoutesMap).forEach((r: any) => {
        if (r.primary) allCoords.push(...r.primary);
      });

      if (allCoords.length > 0) {
        const bounds = L.latLngBounds(allCoords);
        map.fitBounds(bounds, {
          paddingTopLeft: [60, 60],
          paddingBottomRight: [60, 60],
          maxZoom: 15,
          animate: true,
          duration: 1.2
        });
      }
    }
  }, [fitAllTrigger, map]);

  // 3. Restablecer zoom a vista completa de Montería
  useEffect(() => {
    if (resetTrigger && resetTrigger > 0) {
      map.setView([8.74798, -75.88143], 13, {
        animate: true,
        duration: 1.0
      });
    }
  }, [resetTrigger, map]);

  return null;
}

export interface RouteItem {
  primary: [number, number][];
  alternatives?: [number, number][][];
  ambulanceId: string;
  incidentId: number;
}

interface MapProps {
  results: any;
  showHospitals: boolean;
  showUnits: boolean;
  showHeatmap?: boolean;
  activeRoutesMap: Record<number, RouteItem>;
  focusedIncidentId?: number | null;
  movingPositions: Record<string, [number, number]>;
  resetTrigger?: number;
  fitAllTrigger?: number;
  focusRouteTrigger?: number;
  onResetView?: () => void;
  onFocusRoute?: () => void;
  onFitAll?: () => void;
}

export default function Map({ 
  results, 
  showHospitals, 
  showUnits, 
  showHeatmap = true,
  activeRoutesMap = {},
  focusedIncidentId = null,
  movingPositions = {},
  resetTrigger = 0,
  fitAllTrigger = 0,
  focusRouteTrigger = 0,
  onResetView,
  onFocusRoute,
  onFitAll
}: MapProps) {
  const position: [number, number] = [8.74798, -75.88143];

  let ambulanceCounter = 1;
  const activeRoutesList = Object.values(activeRoutesMap);
  const hasMultipleRoutes = activeRoutesList.length > 1;

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      
      {/* Botones flotantes de control de cámara y navegación multi-ruta */}
      <div className="map-camera-controls" style={{
        position: 'absolute',
        bottom: '1.5rem',
        left: '1.5rem',
        zIndex: 1000,
        display: 'flex',
        gap: '0.6rem',
        flexWrap: 'wrap',
        pointerEvents: 'auto'
      }}>
        {activeRoutesList.length > 0 && (
          <button
            onClick={onFocusRoute}
            style={{
              background: '#2563eb',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              padding: '0.55rem 0.95rem',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              boxShadow: '0 4px 12px rgba(37, 99, 235, 0.35)',
              transition: 'all 0.2s'
            }}
            title="Enfocar la ambulancia y ruta seleccionada"
          >
            <span>Centrar ruta activa</span>
          </button>
        )}

        {hasMultipleRoutes && (
          <button
            onClick={onFitAll}
            style={{
              background: '#0f172a',
              color: '#38bdf8',
              border: '1px solid #0284c7',
              borderRadius: '8px',
              padding: '0.55rem 0.95rem',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              boxShadow: '0 4px 12px rgba(15, 23, 42, 0.4)',
              transition: 'all 0.2s'
            }}
            title="Encuadrar todas las emergencias activas a la vez"
          >
            <span>Ver todas las emergencias ({activeRoutesList.length})</span>
          </button>
        )}

        <button
          onClick={onResetView}
          style={{
            background: 'rgba(255, 255, 255, 0.96)',
            color: '#0f172a',
            border: '1px solid #cbd5e1',
            borderRadius: '8px',
            padding: '0.55rem 0.95rem',
            fontSize: '0.82rem',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
            backdropFilter: 'blur(4px)',
            transition: 'all 0.2s'
          }}
          title="Ver toda la ciudad de Montería"
        >
          <span>Vista completa de Montería</span>
        </button>
      </div>

      <MapContainer 
        center={position} 
        zoom={13} 
        style={{ height: '100%', width: '100%', zIndex: 1 }}
      >
        <MapCameraController 
          activeRoutesMap={activeRoutesMap}
          focusedIncidentId={focusedIncidentId}
          resetTrigger={resetTrigger}
          fitAllTrigger={fitAllTrigger}
          focusRouteTrigger={focusRouteTrigger}
        />

        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Renderizado de Múltiples Rutas Concurrentes */}
        {activeRoutesList.map((routeItem) => {
          const isFocused = (activeRoutesList.length === 1) || (Number(routeItem.incidentId) === Number(focusedIncidentId));

          return (
            <React.Fragment key={`multi-route-${routeItem.incidentId}`}>
              {/* Alternativas en gris solo para la ruta actualmente enfocada */}
              {isFocused && routeItem.alternatives && routeItem.alternatives.map((altCoords, aIdx) => (
                <Polyline
                  key={`alt-route-${routeItem.incidentId}-${aIdx}`}
                  positions={altCoords}
                  pathOptions={{
                    color: '#64748b',
                    weight: 4,
                    opacity: 0.8,
                    dashArray: '8 6',
                    lineCap: 'round'
                  }}
                />
              ))}

              {/* Trazado principal: azul brillante si está enfocada, cian distinguido si es otra activa */}
              {routeItem.primary && (
                <Polyline
                  positions={routeItem.primary}
                  pathOptions={{
                    color: isFocused ? '#2563eb' : '#0284c7',
                    weight: isFocused ? 6 : 4,
                    opacity: isFocused ? 0.95 : 0.75,
                    dashArray: isFocused ? undefined : '8 4',
                    lineCap: 'round',
                    lineJoin: 'round'
                  }}
                />
              )}
            </React.Fragment>
          );
        })}

        {/* Nodos de Demanda (Zonas de Emergencia - Heatmap Compacto) */}
        {showHeatmap && results && results.node_coords && results.node_coords.map((coord: [number, number], idx: number) => {
          const zoneName = results.node_names ? results.node_names[idx] : `Zona de Demanda ${idx + 1}`;
          return (
            <CircleMarker 
              key={`node-${idx}`} 
              center={coord} 
              radius={10} 
              color="#ea580c" 
              weight={1.5}
              fillColor="#f97316" 
              fillOpacity={0.35}
            >
              <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
                <span><strong>{zoneName}</strong><br/><small style={{color: '#64748b'}}>Zona de Demanda Vial</small></span>
              </Tooltip>
              <Popup>
                <div style={{ textAlign: 'center' }}>
                  <b style={{ color: '#ea580c' }}>{zoneName}</b><br/>
                  <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Zona de concentración de siniestros</span>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}

        {/* Bases Hospitalarias (Cuadrados Azules H) y Puntos Tácticos en Vía (Círculos Verdes B) */}
        {showHospitals && results && results.base_coords && results.base_coords.map((coord: [number, number], idx: number) => {
          const baseName = results.base_names ? results.base_names[idx] : `Base #${idx + 1}`;
          const baseType = results.base_types ? results.base_types[idx] : 'Hospital/Clínica';
          const isTactical = !baseType.toLowerCase().includes('hospital') && !baseType.toLowerCase().includes('clínica') && !baseType.toLowerCase().includes('clinica');

          return (
            <Marker 
              key={`base-${idx}`} 
              position={coord} 
              icon={isTactical ? createTacticalBaseIcon() : createHospitalIcon()}
            >
              <Tooltip direction="top" offset={[0, -11]} opacity={0.95}>
                <span>
                  <strong>{baseName}</strong><br/>
                  <small style={{ color: isTactical ? '#059669' : '#1d4ed8', fontWeight: 600 }}>
                    {isTactical ? 'Punto de Espera Táctica en Vía Pública' : 'Base Hospitalaria Estratégica'}
                  </small>
                </span>
              </Tooltip>
              <Popup>
                <div style={{ textAlign: 'center' }}>
                  <b style={{ color: isTactical ? '#059669' : '#1d4ed8', fontSize: '0.92rem' }}>{baseName}</b><br/>
                  <span style={{ fontSize: '0.8rem', color: '#475569' }}>
                    {isTactical ? 'Punto táctico de espera y patrullaje en vía' : 'Base hospitalaria estratégica'}
                  </span>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Unidades (Ambulancias) Asignadas en Base */}
        {showUnits && results && results.base_coords && results.base_coords.map((coord: [number, number], idx: number) => {
          const asignadas = results.allocation[`${idx}`] || results.allocation[idx] || 0;
          const baseName = results.base_names ? results.base_names[idx] : `Base #${idx + 1}`;
          
          const markers = [];
          for (let i = 0; i < asignadas; i++) {
            const ambNum = ambulanceCounter;
            const label = `A${ambNum}`;
            const formattedId = `APH-${String(ambNum).padStart(2, '0')}`;
            
            // Si la unidad está en movimiento por la vía, no se duplica en la base
            const isMovingThis = !!movingPositions[formattedId];
            if (isMovingThis) {
              ambulanceCounter++;
              continue;
            }

            const displayCoord: [number, number] = [
              coord[0] + 0.0007 + (i * 0.0005), 
              coord[1] + 0.0007 + (i * 0.0005)
            ];

            markers.push(
              <Marker 
                key={`amb-parked-${idx}-${i}`} 
                position={displayCoord} 
                icon={createAmbulanceIcon(label, false)}
              >
                <Tooltip direction="top" offset={[0, -11]} opacity={0.95}>
                  <span><strong>{formattedId} ({label})</strong><br/><small style={{ color: '#ef4444' }}>En base disponible</small></span>
                </Tooltip>
                <Popup>
                  <div style={{ textAlign: 'center' }}>
                    <b style={{ color: '#ef4444', fontSize: '1rem' }}>Ambulancia {formattedId}</b><br/>
                    <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
                      Estacionada en: {baseName}
                    </span>
                  </div>
                </Popup>
              </Marker>
            );
            ambulanceCounter++;
          }
          return markers;
        })}

        {/* Unidades (Ambulancias) en Desplazamiento Activo por la Red Vial */}
        {Object.entries(movingPositions).map(([ambId, pos]) => {
          const ambNum = ambId.replace('APH-', 'A');
          return (
            <Marker
              key={`moving-live-${ambId}`}
              position={pos}
              icon={createAmbulanceIcon(ambNum, true)}
              zIndexOffset={2000}
            >
              <Tooltip direction="top" offset={[0, -13]} opacity={0.95} permanent>
                <span><strong>{ambId}</strong> · En camino</span>
              </Tooltip>
              <Popup>
                <div style={{ textAlign: 'center' }}>
                  <b style={{ color: '#2563eb', fontSize: '1rem' }}>Ambulancia {ambId}</b><br/>
                  <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
                    En camino hacia la escena del siniestro vial
                  </span>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {!results && (
          <Marker position={position}>
            <Popup>Centro de Montería<br/>(Ajusta los parámetros y genera el despliegue)</Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
