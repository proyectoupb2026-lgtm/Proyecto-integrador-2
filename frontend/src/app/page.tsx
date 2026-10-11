"use client";

import React, { useState, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { 
  Clock, Truck, Building2, ChevronLeft, ChevronRight, Activity, X,
  Sliders, Route, BarChart3, ArrowRight, Check, MapPin, ShieldCheck, 
  TrendingUp, AlertTriangle, Layers, Flame, Navigation, ChevronUp, ChevronDown
} from 'lucide-react';

import { API_BASE_URL } from '../config/api';

const DynamicMap = dynamic(() => import('../components/Map'), {
  ssr: false,
  loading: () => <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Cargando mapa en vivo...</div>
});

export default function Home() {
  const [step, setStep] = useState(0); // 0: Landing Hero, 1: App Shell (Tabs)
  const [activeTab, setActiveTab] = useState<'configuracion' | 'operaciones' | 'resultados'>('configuracion');
  
  const [numAmbulances, setNumAmbulances] = useState(8);
  const [traffic, setTraffic] = useState<'fluido' | 'pico'>('fluido');
  const [deploymentStrategy, setDeploymentStrategy] = useState<'todas' | 'hospitales'>('todas');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  // Modal "¿Cómo funciona?"
  const [showHowItWorks, setShowHowItWorks] = useState(false);
  const [tooltipHover, setTooltipHover] = useState(false);

  // Live clock
  const [currentTime, setCurrentTime] = useState<Date | null>(null);

  useEffect(() => {
    setCurrentTime(new Date());
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Map layer toggles
  const [showHospitals, setShowHospitals] = useState(true);
  const [showUnits, setShowUnits] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showMapControls, setShowMapControls] = useState(true);

  // Multi-ruta, multi-ambulancia y control de cámara
  const [activeRoutesMap, setActiveRoutesMap] = useState<Record<number, any>>({});
  const [movingPositions, setMovingPositions] = useState<Record<string, [number, number]>>({});
  const [focusedIncidentId, setFocusedIncidentId] = useState<number | null>(null);
  const [focusRouteTrigger, setFocusRouteTrigger] = useState(0);
  const [fitAllTrigger, setFitAllTrigger] = useState(0);
  const [mapResetTrigger, setMapResetTrigger] = useState(0);

  // Panel toggles
  const [showLeftPanel, setShowLeftPanel] = useState(true);
  const [showRightPanel, setShowRightPanel] = useState(true);

  // Fleet and Incident state
  const [fleet, setFleet] = useState<any[]>([]);
  const [incidents, setIncidents] = useState<any[]>([]);
  const incidentCounterRef = React.useRef(1);

  const fallbackZonas = [
    "Glorieta de Mocarí", "Los Garzones", "Universidad de Córdoba", 
    "Av. Circunvalar", "Sector Centro", "Terminal de Transportes", 
    "Cantaclaro", "La Granja", "Mogambo", "Rancho Grande", "El Dorado", 
    "Los Pericos", "Loma Grande"
  ];
  
  const activeZonas = results?.node_names || fallbackZonas;
  const [selectedZone, setSelectedZone] = useState("0");

  const handleRunModel = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          num_ambulances: numAmbulances,
          num_nodes: 0,
          num_bases: 0,
          t_max: 10.0,
          alpha: 0.5,
          strategy: deploymentStrategy
        })
      });
      const data = await response.json();
      if (data.status === "success") {
        setResults(data);
        
        // Inicializar Flota
        const newFleet: any[] = [];
        let ambId = 1;
        data.base_coords.forEach((coord: any, baseIdx: number) => {
          const count = data.allocation[baseIdx] || 0;
          for (let i = 0; i < count; i++) {
            const formattedId = `APH-${String(ambId).padStart(2, '0')}`;
            newFleet.push({ 
              id: formattedId, 
              baseIdx, 
              baseName: data.base_names[baseIdx],
              baseType: data.base_types ? data.base_types[baseIdx] : 'Hospital/Clínica',
              status: 'available', 
              coord 
            });
            ambId++;
          }
        });
        setFleet(newFleet);
        setIncidents([]);
        setActiveRoutesMap({});
        setMovingPositions({});
        setFocusedIncidentId(null);
        setActiveTab('operaciones');
      } else {
        alert("Error del modelo: " + data.detail);
      }
    } catch (err) {
      console.error(err);
      alert("Error conectando con la API (Puerto 8000). Asegúrate de que FastAPI esté corriendo.");
    } finally {
      setLoading(false);
    }
  };

  // Rutas activas filtradas: solo mostramos en el mapa las rutas de incidentes activos en fase de despacho o viaje (pasos 1, 2, 3)
  const sanitizedRoutesMap = useMemo(() => {
    const inTransitIds = new Set(
      incidents
        .filter(i => i.stepProgress <= 3)
        .map(i => i.id)
    );
    const clean: Record<number, any> = {};
    Object.entries(activeRoutesMap).forEach(([k, v]) => {
      const numKey = Number(k);
      if (inTransitIds.has(numKey)) {
        clean[numKey] = v;
      }
    });
    return clean;
  }, [activeRoutesMap, incidents]);

  // Finalizar y limpiar de inmediato un incidente, liberando su ambulancia y borrando su ruta del mapa
  const dismissIncident = (id: number) => {
    // 1. Quitar el incidente de la lista y liberar su ambulancia asociada
    setIncidents(prev => {
      const inc = prev.find(i => i.id === id);
      const ambId = inc ? inc.assignedAmbulance : null;
      if (ambId) {
        setFleet(fPrev => fPrev.map(a => a.id === ambId ? { ...a, status: 'available' } : a));
        setMovingPositions(mPrev => {
          const updated = { ...mPrev };
          delete updated[ambId];
          return updated;
        });
      }
      return prev.filter(i => i.id !== id);
    });

    // 2. Eliminar inmediatamente la ruta del mapa
    setActiveRoutesMap(prev => {
      const updated = { ...prev };
      delete updated[id];
      return updated;
    });

    // 3. Resetear foco de cámara si estaba enfocado
    setFocusedIncidentId(prev => (Number(prev) === Number(id) ? null : prev));
  };

  const reportNewAccident = async () => {
    if (!results) {
      alert("Por favor genera primero el despliegue de la flota.");
      return;
    }

    const idx = parseInt(selectedZone);
    const zonaName = activeZonas[idx];
    const accLoc = results.node_coords[idx];
    
    // 1. Identificar todas las ambulancias actualmente comprometidas en emergencias activas
    const busyAmbulanceIds = new Set(
      incidents
        .filter(inc => inc.status !== 'completed')
        .map(inc => inc.assignedAmbulance)
    );

    // 2. Buscar ambulancia disponible más cercana que no esté en servicio ni pre-asignada
    const availableAmbs = fleet.filter(a => a.status === 'available' && !busyAmbulanceIds.has(a.id));
    if (availableAmbs.length === 0) {
      alert("No hay ambulancias disponibles en este momento. Todas las unidades activas están atendiendo emergencias.");
      return;
    }

    let nearest = availableAmbs[0];
    let minD = Infinity;
    availableAmbs.forEach(a => {
      const d = Math.hypot(a.coord[0] - accLoc[0], a.coord[1] - accLoc[1]);
      if (d < minD) { minD = d; nearest = a; }
    });

    // 3. Reservar INMEDIATAMENTE la unidad para evitar que clics rápidos la asignen dos veces
    setFleet(prev => prev.map(a => a.id === nearest.id ? { ...a, status: 'pre-assigned' } : a));

    const factorTrafico = traffic === 'pico' ? 1.6 : 1.0;
    let travelTimeMin = Math.max(2, Math.round(minD * 180 * factorTrafico));
    let distanceKm = 0;
    let primaryPath: [number, number][] = [nearest.coord, accLoc];
    let altPaths: [number, number][][] = [];

    // Consultar rutas navegables reales y alternativas al backend
    try {
      const routeRes = await fetch(`${API_BASE_URL}/api/route`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_lat: nearest.coord[0],
          start_lon: nearest.coord[1],
          end_lat: accLoc[0],
          end_lon: accLoc[1],
          speed_kmh: 30.0,
          traffic_factor: factorTrafico
        })
      });
      const routeData = await routeRes.json();
      if (routeData.status === 'success') {
        primaryPath = routeData.primary_route.path_coords;
        altPaths = routeData.alternative_routes.map((r: any) => r.path_coords);
        travelTimeMin = routeData.primary_route.travel_time_min;
        distanceKm = routeData.primary_route.distance_km;
      }
    } catch (e) {
      console.warn("Fallo cálculo ruta vía API:", e);
    }

    const newId = incidentCounterRef.current++;

    // Agregar la nueva ruta al diccionario de rutas activas concurrentes
    setActiveRoutesMap(prev => ({
      ...prev,
      [newId]: {
        primary: primaryPath,
        alternatives: altPaths,
        ambulanceId: nearest.id,
        incidentId: newId
      }
    }));

    // Enfocar automáticamente la nueva emergencia en el mapa
    setFocusedIncidentId(newId);
    setFocusRouteTrigger(prev => prev + 1);

    // Actualización funcional para garantizar consistencia con incidentes existentes
    setIncidents(prev => [{
      id: newId,
      loc: zonaName,
      assignedAmbulance: nearest.id,
      simulatedMins: travelTimeMin,
      distanceKm: distanceKm,
      priority: 'PRIORIDAD ALTA',
      category: 'Accidente de tránsito',
      stepProgress: 1, // 1: Llamada, 2: Despacho, 3: En camino, 4: En escena, 5: Regreso
      timeDesc: 'hace 1 min',
      desc: `Ambulancia ${nearest.id} asignada (${distanceKm > 0 ? distanceKm + ' km · ' : ''}${travelTimeMin} min est.)`,
      pathCoords: primaryPath,
      status: 'pending'
    }, ...prev]);
  };

  const dispatchAmbulance = (id: number) => {
    const inc = incidents.find(i => i.id === id);
    if (!inc) return;

    const mins = inc.simulatedMins || 3;
    // Escala de tiempo ágil y visible: entre 6 y 14 segundos
    const moveDurationMs = Math.min(14000, Math.max(6000, mins * 2500));

    // Paso 2: Despacho de la unidad
    setIncidents(curr => curr.map(i => 
      i.id === id ? { 
        ...i, 
        stepProgress: 2, 
        status: 'en-route', 
        desc: `Unidad despachada desde su base` 
      } : i
    ));
    setFleet(prev => prev.map(a => a.id === inc.assignedAmbulance ? { ...a, status: 'busy' } : a));

    // A los 1.2s pasa a Paso 3: En camino hacia la escena y arranca la simulación de movimiento
    setTimeout(() => {
      setIncidents(curr => curr.map(i => 
        i.id === id ? { 
          ...i, 
          stepProgress: 3, 
          desc: `En camino hacia la escena (~${mins} min)` 
        } : i
      ));

      // Animación en tiempo real del avance concurrente e independiente de esta ambulancia
      const path: [number, number][] = inc.pathCoords || [];
      if (path.length > 1) {
        const startTime = Date.now();
        const animTimer = setInterval(() => {
          const elapsed = Date.now() - startTime;
          const progress = Math.min(1, elapsed / moveDurationMs);
          
          const totalSegments = path.length - 1;
          const floatIndex = progress * totalSegments;
          const idxA = Math.floor(floatIndex);
          const idxB = Math.min(totalSegments, idxA + 1);
          const fraction = floatIndex - idxA;
          
          const ptA = path[idxA];
          const ptB = path[idxB];
          const curLat = ptA[0] + (ptB[0] - ptA[0]) * fraction;
          const curLon = ptA[1] + (ptB[1] - ptA[1]) * fraction;

          // Actualiza la posición de ESTA ambulancia en el mapa sin alterar las demás
          setMovingPositions(prev => ({
            ...prev,
            [inc.assignedAmbulance]: [curLat, curLon]
          }));

          // Llegada a escena al completar el 100% de la ruta
          if (progress >= 1) {
            clearInterval(animTimer);

            // Fijar posición en la escena
            setMovingPositions(prev => ({
              ...prev,
              [inc.assignedAmbulance]: path[path.length - 1]
            }));

            // La ambulancia llegó a la escena: retiramos la ruta del mapa de inmediato
            setActiveRoutesMap(prev => {
              const updated = { ...prev };
              delete updated[id];
              return updated;
            });

            // Paso 4: En escena (Atención Prehospitalaria en curso)
            setIncidents(curr => curr.map(i => 
              i.id === id ? { 
                ...i, 
                stepProgress: 4, 
                status: 'attended', 
                priority: 'ATENCIÓN EN CURSO', 
                desc: `Atención médica en escena · Estabilizando paciente` 
              } : i
            ));

            // 5 segundos en escena realizando atención
            setTimeout(() => {
              // Paso 5: Regreso / Traslado
              setIncidents(curr => curr.map(i => 
                i.id === id ? { 
                  ...i, 
                  stepProgress: 5, 
                  desc: `Traslado médico completado · Regresando a base` 
                } : i
              ));

              // 4 segundos de retorno y la unidad vuelve a quedar disponible
              setTimeout(() => {
                dismissIncident(id);
              }, 4000);

            }, 5000);
          }
        }, 50); // 20 frames por segundo para animación fluida
      } else {
        setTimeout(() => {
          dismissIncident(id);
        }, 3000);
      }
    }, 1200);
  };

  const completeIncidentEarly = (id: number) => {
    // 1. Quitar la ruta del mapa
    setActiveRoutesMap(prev => {
      const updated = { ...prev };
      delete updated[id];
      return updated;
    });

    // 2. Pasar a paso 5 (Regreso)
    setIncidents(curr => curr.map(i => 
      i.id === id ? { 
        ...i, 
        stepProgress: 5, 
        desc: `Traslado médico finalizado · Regresando a base` 
      } : i
    ));

    // A los 2.5 segundos se libera automáticamente si el usuario no pulsa finalizar antes
    setTimeout(() => {
      dismissIncident(id);
    }, 2500);
  };

  // Modal instructivo "¿Cómo funciona?"
  const renderHowItWorksModal = () => {
    if (!showHowItWorks) return null;
    return (
      <div className="modal-overlay" onClick={() => setShowHowItWorks(false)}>
        <div className="modal-card" onClick={e => e.stopPropagation()}>
          <button className="modal-close-btn" onClick={() => setShowHowItWorks(false)} title="Cerrar">
            <X size={20} />
          </button>

          <div style={{ color: '#2563eb', fontSize: '0.8rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            CÓMO FUNCIONA
          </div>
          <h2 style={{ fontSize: '1.9rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.5rem' }}>
            De los datos al despacho, en tres pasos.
          </h2>
          <p style={{ color: '#64748b', fontSize: '1rem', maxWidth: '620px', lineHeight: 1.5 }}>
            APH Montería transforma las condiciones operativas y la siniestralidad vial en una distribución de ambulancias lista para supervisar en tiempo real.
          </p>

          <div className="modal-grid">
            <div className="step-card">
              <div className="step-card-header">
                <div className="step-icon-box">
                  <Sliders size={22} />
                </div>
                <span className="step-num">01</span>
              </div>
              <div className="step-card-title">Configure</div>
              <div className="step-card-desc">
                Indique la capacidad real de su flota (hasta 27 ambulancias), el tipo de despliegue en la ciudad y las condiciones del tráfico urbano.
              </div>
            </div>

            <div className="step-card">
              <div className="step-card-header">
                <div className="step-icon-box">
                  <Route size={22} />
                </div>
                <span className="step-num">02</span>
              </div>
              <div className="step-card-title">Mejore</div>
              <div className="step-card-desc">
                El modelo matemático (MILP) evalúa la red vial, la demanda histórica en las 21 zonas y tiempos de viaje para proponer una distribución eficiente.
              </div>
            </div>

            <div className="step-card">
              <div className="step-card-header">
                <div className="step-icon-box">
                  <BarChart3 size={22} />
                </div>
                <span className="step-num">03</span>
              </div>
              <div className="step-card-title">Supervise</div>
              <div className="step-card-desc">
                Monitoree cada unidad sobre el mapa interactivo con auto-enfoque, asigne emergencias por cercanía inmediata y supervise el ciclo completo de despacho.
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <button 
              onClick={() => setShowHowItWorks(false)}
              style={{ background: '#2563eb', color: 'white', border: 'none', padding: '0.75rem 1.8rem', borderRadius: '10px', fontWeight: 600, fontSize: '0.95rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)' }}
            >
              Entendido <Check size={18} />
            </button>
          </div>
        </div>
      </div>
    );
  };

  // ----------------------------------------------------
  // STEP 0: Landing Hero (Portada con mapa vectorial difuminado)
  // ----------------------------------------------------
  if (step === 0) {
    return (
      <div className="hero-layout" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#ffffff', position: 'relative', overflow: 'hidden' }}>
        
        {/* Mapa vectorial de fondo difuminado horizontalmente hacia la izquierda */}
        <div style={{
          position: 'absolute',
          top: 0,
          right: 0,
          bottom: 0,
          width: '75%',
          zIndex: 1,
          pointerEvents: 'none',
          WebkitMaskImage: 'linear-gradient(to right, transparent 0%, rgba(0,0,0,0.6) 30%, black 100%)',
          maskImage: 'linear-gradient(to right, transparent 0%, rgba(0,0,0,0.6) 30%, black 100%)'
        }}>
          <svg viewBox="0 0 900 650" style={{ width: '100%', height: '100%', objectFit: 'cover' }}>
            <defs>
              <linearGradient id="curveGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.3" />
                <stop offset="50%" stopColor="#2563eb" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#1d4ed8" stopOpacity="1" />
              </linearGradient>
              <filter id="shadowGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="6" stdDeviation="8" floodColor="#2563eb" floodOpacity="0.25" />
              </filter>
              <pattern id="gridPat" width="35" height="35" patternUnits="userSpaceOnUse">
                <path d="M 0 0 L 17 17 L 0 35 Z" fill="#f8fafc" stroke="#f1f5f9" strokeWidth="1" />
              </pattern>
            </defs>

            <rect x="0" y="0" width="900" height="650" fill="url(#gridPat)" opacity="0.6" />

            {/* Arterias viales principales de Montería */}
            <path d="M 60 580 Q 380 500 880 340" fill="none" stroke="#f1f5f9" strokeWidth="48" strokeLinecap="round" />
            <path d="M 80 480 Q 420 380 820 80" fill="none" stroke="#e2e8f0" strokeWidth="22" strokeLinecap="round" opacity="0.75" />
            <path d="M 180 580 Q 520 440 880 160" fill="none" stroke="#e2e8f0" strokeWidth="12" strokeLinecap="round" opacity="0.6" />

            {/* Nombres viales y de referencia */}
            <text x="640" y="70" fill="#94a3b8" fontSize="13" fontWeight="700" letterSpacing="0.08em">GLORIETA DE MOCARÍ</text>
            <text x="420" y="325" fill="#cbd5e1" fontSize="11" fontWeight="600" letterSpacing="0.06em" transform="rotate(-18 420 325)">AV. CIRCUNVALAR</text>
            <text x="560" y="475" fill="#94a3b8" fontSize="12" fontWeight="700" letterSpacing="0.06em">UNIVERSIDAD DE CÓRDOBA</text>

            {/* Trazado de ruta en curva azul luminosa */}
            <path d="M 360 510 Q 580 440 790 185" fill="none" stroke="#94a3b8" strokeWidth="3" strokeDasharray="8 8" opacity="0.7" />
            <path 
              d="M 220 540 Q 500 400 790 185" 
              fill="none"
              stroke="url(#curveGradient)" 
              strokeWidth="5.5" 
              strokeLinecap="round"
              filter="url(#shadowGlow)"
            />

            {/* Ambulancia en trayecto (Vector limpio sin emojis) */}
            <g transform="translate(490, 290)">
              <rect width="44" height="40" rx="10" fill="#ffffff" stroke="#bfdbfe" strokeWidth="2" filter="drop-shadow(0 4px 10px rgba(0,0,0,0.08))" />
              <rect x="2" y="2" width="40" height="36" rx="8" fill="#eff6ff" />
              <path d="M 12 25 L 16 17 L 27 17 L 31 22 L 34 22 L 34 25 Z" fill="#2563eb" />
              <rect x="12" y="22" width="20" height="7" fill="#2563eb" />
              <circle cx="17" cy="29" r="3" fill="#1e293b" />
              <circle cx="28" cy="29" r="3" fill="#1e293b" />
              <rect x="18" y="20" width="8" height="2.5" fill="#ef4444" rx="1" />
            </g>

            {/* Siniestro vial en el destino (Pinpoint vectorial limpio) */}
            <g transform="translate(770, 160)">
              <rect width="48" height="44" rx="12" fill="#fee2e2" stroke="#fca5a5" strokeWidth="2" filter="drop-shadow(0 6px 14px rgba(239, 68, 68, 0.25))" />
              <path d="M 24 13 C 20 13 17 16 17 20 C 17 25 24 32 24 32 C 24 32 31 25 31 20 C 31 16 28 13 24 13 Z" fill="#ef4444" />
              <circle cx="24" cy="19" r="2.5" fill="#ffffff" />
            </g>
          </svg>
        </div>

        {/* Top Navbar */}
        <header style={{ height: '75px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 3.5rem', zIndex: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ background: '#0f3460', color: 'white', padding: '0.55rem', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Truck size={20} />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '1.15rem', color: '#0f172a', lineHeight: 1.1 }}>APH Montería</div>
              <div style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Centro de Operaciones</div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#334155' }}>
              {currentTime ? currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
            </div>
          </div>
        </header>

        {/* Hero Content (Lado Izquierdo) */}
        <main style={{ flex: 1, display: 'flex', alignItems: 'center', padding: '0 4rem', zIndex: 10 }}>
          <div style={{ maxWidth: '580px', paddingBottom: '2rem' }}>
            <div className="hero-badge-pill">
              <span className="hero-badge-dot"></span>
              CENTRO DE OPERACIONES ACTIVO
            </div>

            <p className="hero-overline">DESPACHO ASISTIDO POR DATOS</p>
            <h1 className="hero-headline">
              La respuesta correcta,<br />en el menor tiempo.
            </h1>
            <p className="hero-subtitle">
              Configure la flota y genere un despliegue asistido por datos para la red de atención prehospitalaria de Montería.
            </p>

            <button 
              className="hero-cta-btn" 
              onClick={() => {
                setStep(1);
                setActiveTab('configuracion');
              }}
            >
              Iniciar <ArrowRight size={20} />
            </button>
          </div>
        </main>

        {/* Botón flotante único (Azul fijo en la esquina inferior derecha) */}
        <div className="fab-container">
          {tooltipHover && (
            <div className="fab-tooltip">
              ¿Cómo funciona?
            </div>
          )}
          <button 
            className="fab-button"
            onMouseEnter={() => setTooltipHover(true)}
            onMouseLeave={() => setTooltipHover(false)}
            onClick={() => setShowHowItWorks(true)}
            title="¿Cómo funciona?"
          >
            <Route size={24} />
          </button>
        </div>

        {renderHowItWorksModal()}
      </div>
    );
  }

  // ----------------------------------------------------
  // APP SHELL (Con las 3 pestañas: Configuración, Operaciones, Resultados)
  // ----------------------------------------------------
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      
      {/* Top Bar Principal (Imagen 1 de Figma) */}
      <header className="app-topbar">
        <div className="app-brand" onClick={() => setStep(0)} title="Volver a la portada">
          <div className="brand-icon">
            <Truck size={20} />
          </div>
          <div>
            <div className="brand-title">APH Montería</div>
            <div className="brand-sub">Centro de Operaciones</div>
          </div>
        </div>

        {/* Las 3 Pestañas Centrales */}
        <nav className="app-tabs">
          <button 
            className={`app-tab-btn ${activeTab === 'configuracion' ? 'active' : ''}`}
            onClick={() => setActiveTab('configuracion')}
          >
            Configuración
          </button>
          <button 
            className={`app-tab-btn ${activeTab === 'operaciones' ? 'active' : ''}`}
            onClick={() => {
              if (!results) {
                alert("Primero debes generar el despliegue en la pestaña de Configuración.");
                return;
              }
              setActiveTab('operaciones');
            }}
          >
            Operaciones
          </button>
          <button 
            className={`app-tab-btn ${activeTab === 'resultados' ? 'active' : ''}`}
            onClick={() => {
              if (!results) {
                alert("Primero debes generar el despliegue para visualizar los resultados matemáticos.");
                return;
              }
              setActiveTab('resultados');
            }}
          >
            Resultados
          </button>
        </nav>

        {/* Estado en Línea */}
        <div className="app-status-badge">
          <span className="app-status-dot"></span>
          Sistema en línea
        </div>
      </header>

      {/* Subheader Informativo (Imagen 1) */}
      <div className="app-subheader">
        <div className="subheader-left">
          <div className="op-status">
            <span className="op-dot"></span>
            Operación normal
          </div>
          <div style={{ height: '16px', width: '1px', background: '#e2e8f0' }}></div>
          <div className="location-tag">
            Montería, Córdoba
          </div>
        </div>

        <div className="subheader-right">
          <div className="clock-display">
            {currentTime ? currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--'}
          </div>

          {activeTab === 'configuracion' && (
            <button className="btn-nav-action" onClick={handleRunModel} disabled={loading}>
              {loading ? 'Procesando...' : 'Generar despliegue →'}
            </button>
          )}

          {activeTab === 'operaciones' && (
            <button className="btn-nav-action" onClick={() => setActiveTab('resultados')}>
              Ver resultados →
            </button>
          )}

          {activeTab === 'resultados' && (
            <button className="btn-nav-action" onClick={() => setActiveTab('operaciones')}>
              Volver al mapa →
            </button>
          )}
        </div>
      </div>

      {/* ----------------------------------------------------
          VENTANA 1: Configuración de la Flota (Con fondo sutil)
          ---------------------------------------------------- */}
      {activeTab === 'configuracion' && (
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '3rem 1.5rem', position: 'relative', background: '#f8fafc' }}>
          
          {/* Fondo sutil del mapa de Montería */}
          <div style={{ position: 'absolute', inset: 0, opacity: 0.09, pointerEvents: 'none', overflow: 'hidden' }}>
            <svg viewBox="0 0 1200 800" style={{ width: '100%', height: '100%', objectFit: 'cover' }}>
              <path d="M 220 0 C 260 250 190 500 240 800" fill="none" stroke="#0284c7" strokeWidth="36" strokeLinecap="round" opacity="0.35" />
              <path d="M 0 580 Q 520 460 1200 310" fill="none" stroke="#2563eb" strokeWidth="18" strokeLinecap="round" />
              <path d="M 120 720 Q 620 410 1120 90" fill="none" stroke="#3b82f6" strokeWidth="14" strokeLinecap="round" />
              <path d="M 320 800 Q 720 520 1200 220" fill="none" stroke="#60a5fa" strokeWidth="10" strokeLinecap="round" />
              <path d="M 240 450 L 950 450" fill="none" stroke="#93c5fd" strokeWidth="8" strokeDasharray="12 12" />
              <circle cx="240" cy="450" r="16" fill="#2563eb" opacity="0.3" />
              <circle cx="680" cy="380" r="20" fill="#ef4444" opacity="0.3" />
              <circle cx="900" cy="240" r="16" fill="#f97316" opacity="0.3" />
            </svg>
          </div>

          <div className="wizard-header" style={{ position: 'relative', zIndex: 2 }}>
            <p className="overline" style={{ color: '#2563eb', fontWeight: 700, fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Centro de Coordinación Médica
            </p>
            <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: '#0f172a', margin: '0.5rem 0' }}>
              Configuración de la Flota APH
            </h1>
            <p className="subtitle" style={{ color: '#64748b', fontSize: '1rem', maxWidth: '580px' }}>
              Sistema inteligente para la mejora y despacho de ambulancias en tiempo real.
            </p>
          </div>

          <div className="wizard-card" style={{ position: 'relative', zIndex: 2 }}>
            <div className="step-indicator">Paso 1 de 2</div>
            <h2>Parámetros de la flota</h2>
            <p>Define la capacidad operativa y la estrategia de posicionamiento sobre la ciudad.</p>

            <div className="form-group">
              <div className="form-label-row">
                <div>
                  <div className="form-label">Ambulancias disponibles</div>
                  <div className="form-desc">Unidades de la red asistencial de Montería (hasta 27)</div>
                </div>
                <div className="counter-control">
                  <button className="counter-btn" onClick={() => setNumAmbulances(Math.max(1, numAmbulances - 1))}>−</button>
                  <input 
                    type="number"
                    min={1}
                    max={27}
                    value={numAmbulances}
                    onChange={e => {
                      const val = parseInt(e.target.value);
                      if (!isNaN(val)) setNumAmbulances(Math.max(1, Math.min(27, val)));
                    }}
                    className="counter-input"
                  />
                  <button className="counter-btn" onClick={() => setNumAmbulances(Math.min(27, numAmbulances + 1))}>+</button>
                </div>
              </div>
            </div>

            {/* Selector de Estrategia de Ubicación de Bases */}
            <div className="form-group">
              <div className="form-label-row">
                <div>
                  <div className="form-label">Estrategia de posicionamiento de bases</div>
                  <div className="form-desc">Define dónde esperan las ambulancias antes de un siniestro</div>
                </div>
              </div>
              <div className="radio-group">
                <div 
                  className={`radio-card ${deploymentStrategy === 'todas' ? 'active' : ''}`} 
                  onClick={() => setDeploymentStrategy('todas')}
                >
                  <div style={{ background: '#eff6ff', color: '#2563eb', padding: '0.65rem', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <ShieldCheck size={22} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#0f172a' }}>Toda la ciudad (Hospitales + Puntos Tácticos en Vía)</div>
                    <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '3px', lineHeight: 1.35 }}>Descentralizado: Margen Izquierda, Glorietas Mocarí y Vacas, Terminal y Sur</div>
                  </div>
                </div>
                <div 
                  className={`radio-card ${deploymentStrategy === 'hospitales' ? 'active' : ''}`} 
                  onClick={() => setDeploymentStrategy('hospitales')}
                >
                  <div style={{ background: '#f8fafc', color: '#64748b', padding: '0.65rem', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Building2 size={22} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#0f172a' }}>Solo Hospitales y Clínicas</div>
                    <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '3px', lineHeight: 1.35 }}>Estacionadas exclusivamente en los 7 centros médicos</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="form-group">
              <div className="form-label-row">
                <div>
                  <div className="form-label">Condiciones de tráfico urbano</div>
                  <div className="form-desc">Impacto en la velocidad media de desplazamiento</div>
                </div>
              </div>
              <div className="radio-group">
                <div className={`radio-card ${traffic === 'fluido' ? 'active' : ''}`} onClick={() => setTraffic('fluido')}>
                  <div style={{ background: '#eff6ff', color: '#2563eb', padding: '0.65rem', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Navigation size={22} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600 }}>Tráfico fluido</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Circulación normal (35 km/h prom.)</div>
                  </div>
                </div>
                <div className={`radio-card ${traffic === 'pico' ? 'active' : ''}`} onClick={() => setTraffic('pico')}>
                  <div style={{ background: '#fff7ed', color: '#ea580c', padding: '0.65rem', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <AlertTriangle size={22} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600 }}>Hora pico</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Alta congestión (factor 1.6x)</div>
                  </div>
                </div>
              </div>
            </div>

            <button className="btn-large" onClick={handleRunModel} disabled={loading}>
              {loading ? 'Calculando distribución asistida...' : 'Generar despliegue de flota →'}
            </button>
          </div>

          {/* Botón flotante único (Azul fijo en la esquina inferior derecha) */}
          <div className="fab-container">
            {tooltipHover && (
              <div className="fab-tooltip">
                ¿Cómo funciona?
              </div>
            )}
            <button 
              className="fab-button"
              onMouseEnter={() => setTooltipHover(true)}
              onMouseLeave={() => setTooltipHover(false)}
              onClick={() => setShowHowItWorks(true)}
              title="¿Cómo funciona?"
            >
              <Route size={24} />
            </button>
          </div>
        </div>
      )}

      {/* ----------------------------------------------------
          VENTANA 2: Operaciones en Vivo (Mapa + Flota en vivo + Despacho)
          ---------------------------------------------------- */}
      {activeTab === 'operaciones' && (
        <div className="dash-content" style={{ position: 'relative', flex: 1, display: 'flex', overflow: 'hidden' }}>
          
          {/* Botones flotantes para re-abrir paneles cuando están ocultos */}
          {!showLeftPanel && (
            <button 
              onClick={() => setShowLeftPanel(true)}
              style={{ position: 'absolute', top: '1.5rem', left: '1rem', zIndex: 1000, background: 'white', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '0.5rem', cursor: 'pointer', boxShadow: 'var(--shadow-md)' }}
              title="Mostrar Flota en Vivo"
            >
              <ChevronRight size={20} />
            </button>
          )}
          {!showRightPanel && (
            <button 
              onClick={() => setShowRightPanel(true)}
              style={{ position: 'absolute', top: '1.5rem', right: '1rem', zIndex: 1000, background: 'white', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '0.5rem', cursor: 'pointer', boxShadow: 'var(--shadow-md)' }}
              title="Mostrar Despacho"
            >
              <ChevronLeft size={20} />
            </button>
          )}

          {/* Panel Izquierdo: "Flota en vivo" con "Indicadores" */}
          {showLeftPanel && (
            <aside className="left-panel">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <div className="panel-title" style={{ marginBottom: 0 }}>Flota en vivo</div>
                <button onClick={() => setShowLeftPanel(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#999' }}>
                  <X size={20} />
                </button>
              </div>
              
              <h2 style={{ fontSize: '1.125rem', marginBottom: '0.25rem', color: '#0f172a' }}>Indicadores</h2>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>Monitoreo en tiempo real</p>

              <div className="metric-card">
                <div className="metric-icon" style={{ background: '#eff6ff', color: '#3b82f6' }}>
                  <Clock size={20} />
                </div>
                <div>
                  <div className="metric-label">Tiempo Medio de Respuesta</div>
                  <div className="metric-val">{results ? (results.avg_time || 2.4).toFixed(1) : 2.4} min</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>Calculado matemáticamente</div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon" style={{ background: '#dcfce7', color: '#10b981' }}>
                  <Truck size={20} />
                </div>
                <div>
                  <div className="metric-label">Ambulancias en servicio</div>
                  <div className="metric-val">{fleet.filter(a => a.status === 'available').length} / 27</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                    {incidents.filter(i => i.stepProgress >= 2 && i.stepProgress < 5).length} en misión ({numAmbulances} activas)
                  </div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon" style={{ background: '#f3e8ff', color: '#9333ea' }}>
                  <Building2 size={20} />
                </div>
                <div>
                  <div className="metric-label">Bases con unidades</div>
                  <div className="metric-val">
                    {results ? Object.values(results.allocation).filter((v:any) => v > 0).length : 6} / {results ? results.base_names.length : 12}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                    {deploymentStrategy === 'todas' ? 'Hospitales y puntos tácticos en vía' : 'Hospitales asignados'}
                  </div>
                </div>
              </div>
            </aside>
          )}

          {/* Centro: Mapa Operativo */}
          <main className="center-panel">
            
            {/* Barra superior de capas (abrible y cerrable) */}
            {showMapControls ? (
              <div className="map-top-bar" style={{ left: showLeftPanel ? '1rem' : '4rem', right: showRightPanel ? '1rem' : '4rem', transition: 'left 0.3s, right 0.3s' }}>
                <div className="live-indicator">
                  <div className="live-dot"></div>
                  <span style={{ fontWeight: 700, color: '#0f172a', fontSize: '0.9rem' }}>Mapa operativo en vivo</span>
                </div>
                
                <div className="map-toggles">
                  <label className="toggle-label">
                    <input type="checkbox" checked={showHospitals} onChange={e => setShowHospitals(e.target.checked)} />
                    <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#1d4ed8' }}>
                      <Building2 size={16} /> Bases / Hospitales
                    </span>
                  </label>
                  <label className="toggle-label">
                    <input type="checkbox" checked={showUnits} onChange={e => setShowUnits(e.target.checked)} />
                    <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#ef4444' }}>
                      <Truck size={16} /> Unidades
                    </span>
                  </label>
                  <label className="toggle-label">
                    <input type="checkbox" checked={showHeatmap} onChange={e => setShowHeatmap(e.target.checked)} />
                    <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#ea580c' }}>
                      <Flame size={16} /> Demanda
                    </span>
                  </label>

                  {/* Botón para cerrar / ocultar la barrita */}
                  <button 
                    onClick={() => setShowMapControls(false)}
                    style={{ background: '#f1f5f9', border: 'none', borderRadius: '6px', padding: '0.25rem 0.55rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: '#64748b' }}
                    title="Ocultar barra de capas"
                  >
                    <ChevronUp size={16} /> Ocultar
                  </button>
                </div>
              </div>
            ) : (
              /* Botón compacto para reabrir la barra de capas */
              <button 
                onClick={() => setShowMapControls(true)}
                style={{ position: 'absolute', top: '1rem', left: showLeftPanel ? '1.5rem' : '4.5rem', zIndex: 1000, background: 'rgba(255,255,255,0.95)', border: '1px solid #cbd5e1', borderRadius: '20px', padding: '0.45rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', fontSize: '0.82rem', fontWeight: 700, color: '#0f172a', backdropFilter: 'blur(4px)' }}
                title="Mostrar capas y controles del mapa"
              >
                <div className="live-dot"></div>
                Mapa operativo en vivo <ChevronDown size={16} />
              </button>
            )}

            <DynamicMap 
              results={results} 
              showHospitals={showHospitals} 
              showUnits={showUnits} 
              showHeatmap={showHeatmap}
              activeRoutesMap={sanitizedRoutesMap}
              focusedIncidentId={focusedIncidentId}
              movingPositions={movingPositions}
              resetTrigger={mapResetTrigger}
              fitAllTrigger={fitAllTrigger}
              focusRouteTrigger={focusRouteTrigger}
              onResetView={() => setMapResetTrigger(prev => prev + 1)}
              onFitAll={() => setFitAllTrigger(prev => prev + 1)}
              onFocusRoute={() => setFocusRouteTrigger(prev => prev + 1)}
            />
          </main>

          {/* Panel Derecho: "Despacho" (con Stepper de 5 pasos como en la Imagen 2 de Figma) */}
          {showRightPanel && (
            <aside className="right-panel">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <div className="panel-title" style={{ marginBottom: 0 }}>Despacho</div>
                <button onClick={() => setShowRightPanel(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#999' }}>
                  <X size={20} />
                </button>
              </div>
              
              {/* Formulario de reporte de emergencia */}
              <div style={{ background: 'white', padding: '1rem', borderRadius: '10px', border: '1px solid var(--color-border)', marginBottom: '1.25rem' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem', color: '#334155' }}>Reportar Nueva Emergencia</div>
                <select 
                  value={selectedZone} 
                  onChange={e => setSelectedZone(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem', marginBottom: '0.65rem', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
                >
                  {activeZonas.map((z: string, idx: number) => (
                    <option key={idx} value={idx}>{z}</option>
                  ))}
                </select>
                <button 
                  onClick={reportNewAccident}
                  style={{ width: '100%', background: '#10b981', color: 'white', border: 'none', padding: '0.6rem', borderRadius: '6px', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                >
                  <Activity size={16} /> Agregar Accidente
                </button>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>Emergencias activas</h2>
                <div style={{ background: '#fee2e2', color: 'var(--color-accent)', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>
                  {incidents.length}
                </div>
              </div>

              {incidents.length === 0 && (
                <div style={{ textAlign: 'center', padding: '2rem 1rem', color: '#94a3b8', fontSize: '0.85rem' }}>
                  No hay incidentes activos en este momento.
                </div>
              )}

              {/* Lista de incidentes con el Stepper idéntico a Figma (Imagen 2) */}
              {incidents.map(inc => {
                const stepsList = ['Llamada', 'Despacho', 'En camino', 'En escena', 'Regreso'];
                const isAttended = inc.stepProgress >= 4;
                const isFocused = (incidents.length === 1) || (Number(focusedIncidentId) === Number(inc.id));

                return (
                  <div 
                    key={inc.id} 
                    className="incident-stepper-card"
                    style={{
                      border: isFocused ? '2px solid #2563eb' : '1px solid var(--color-border)',
                      boxShadow: isFocused ? '0 0 14px rgba(37,99,235,0.18)' : undefined,
                      transition: 'all 0.25s'
                    }}
                  >
                    <div className="stepper-header">
                      <div className="stepper-header-left">
                        <div className={`stepper-badge-icon ${isAttended ? 'blue' : 'red'}`}>
                          {isAttended ? <Check size={20} /> : <MapPin size={20} />}
                        </div>
                        <div>
                          <div className={`stepper-overline ${isAttended ? 'orange' : 'red'}`}>
                            {isAttended ? 'ATENCIÓN EN CURSO' : 'PRIORIDAD ALTA'}
                          </div>
                          <div className="stepper-title">{inc.loc}</div>
                          <div className="stepper-subtitle">
                            {inc.category} · {inc.timeDesc || 'hace 2 min'}
                          </div>
                        </div>
                      </div>
                      
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                          <div className="stepper-amb-tag">
                            {inc.assignedAmbulance}
                          </div>
                          <button
                            onClick={() => dismissIncident(inc.id)}
                            title="Finalizar emergencia y liberar unidad"
                            style={{
                              background: '#fee2e2',
                              border: 'none',
                              color: '#ef4444',
                              borderRadius: '4px',
                              padding: '2px 4px',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              lineHeight: 1
                            }}
                          >
                            <X size={13} />
                          </button>
                        </div>
                        <button
                          onClick={() => {
                            setFocusedIncidentId(inc.id);
                            setFocusRouteTrigger(prev => prev + 1);
                          }}
                          style={{
                            background: isFocused ? '#2563eb' : '#f1f5f9',
                            color: isFocused ? '#ffffff' : '#334155',
                            border: 'none',
                            borderRadius: '4px',
                            padding: '2px 6px',
                            fontSize: '0.68rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '3px'
                          }}
                          title="Enfocar esta ambulancia en el mapa"
                        >
                          {isFocused ? 'Enfocada en mapa' : 'Enfocar en mapa'}
                        </button>
                      </div>
                    </div>

                    {/* Timeline Horizontal Stepper */}
                    <div className="timeline-track">
                      <div className="timeline-line">
                        <div 
                          className="timeline-line-progress" 
                          style={{ width: `${Math.min(100, Math.max(0, ((inc.stepProgress - 1) / 4) * 100))}%` }}
                        ></div>
                      </div>

                      {stepsList.map((st, sIdx) => {
                        const isCurrent = inc.stepProgress === sIdx + 1;
                        const isActive = inc.stepProgress >= sIdx + 1;

                        return (
                          <div key={st} className="timeline-step">
                            <div className={`timeline-dot ${isActive ? (isCurrent ? 'active-center' : 'active') : ''}`}></div>
                            <span className={`timeline-dot-label ${isActive ? 'active' : ''}`}>{st}</span>
                          </div>
                        );
                      })}
                    </div>

                    {/* Botón de Despachar únicamente en paso 1 (Llamada recibida) */}
                    {inc.stepProgress === 1 && (
                      <button 
                        onClick={() => dispatchAmbulance(inc.id)}
                        className="btn-dispatch" 
                        style={{ marginTop: '0.85rem' }}
                      >
                        <Truck size={16} /> Despachar {inc.assignedAmbulance}
                      </button>
                    )}

                    {/* Durante la atención médica en escena (Paso 4) */}
                    {inc.stepProgress === 4 && (
                      <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', fontSize: '0.76rem', color: '#0284c7', fontWeight: 600, background: '#f0f9ff', padding: '5px 8px', borderRadius: '6px', border: '1px solid #bae6fd' }}>
                          <Activity size={14} />
                          <span>Atendiendo paciente en escena</span>
                        </div>
                        <button
                          onClick={() => completeIncidentEarly(inc.id)}
                          style={{
                            background: '#eff6ff',
                            color: '#1d4ed8',
                            border: '1px solid #bfdbfe',
                            borderRadius: '6px',
                            padding: '0.45rem 0.6rem',
                            fontSize: '0.74rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '4px'
                          }}
                        >
                          <Check size={14} /> Iniciar retorno a base
                        </button>
                      </div>
                    )}

                    {/* Durante el regreso o traslado final (Paso 5) */}
                    {inc.stepProgress === 5 && (
                      <div style={{ marginTop: '0.75rem' }}>
                        <button
                          onClick={() => dismissIncident(inc.id)}
                          style={{
                            width: '100%',
                            background: '#f0fdf4',
                            color: '#15803d',
                            border: '1px solid #bbf7d0',
                            borderRadius: '6px',
                            padding: '0.45rem 0.6rem',
                            fontSize: '0.74rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '4px'
                          }}
                        >
                          <Check size={14} /> Finalizar servicio y liberar {inc.assignedAmbulance}
                        </button>
                      </div>
                    )}

                    {/* Descripción de estado en tiempo real */}
                    <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '0.5rem', textAlign: 'center' }}>
                      {inc.desc}
                    </div>
                  </div>
                );
              })}
            </aside>
          )}
        </div>
      )}

      {/* ----------------------------------------------------
          VENTANA 3: Resultados y Análisis Matemático
          ---------------------------------------------------- */}
      {activeTab === 'resultados' && (
        <div style={{ flex: 1, overflowY: 'auto', padding: '2.5rem', background: '#f8fafc' }}>
          <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
            
            <div style={{ marginBottom: '2rem' }}>
              <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.25rem' }}>
                Resultados del Despliegue y Cobertura Operativa
              </h1>
              <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
                Métricas calculadas por el modelo matemático aplicadas a las 21 zonas de demanda y las bases estratégicas de Montería.
              </p>
            </div>

            {/* KPI Cards de Resultados */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.25rem', marginBottom: '2.5rem' }}>
              <div style={{ background: 'white', padding: '1.5rem', borderRadius: '14px', border: '1px solid #e2e8f0', boxShadow: 'var(--shadow-sm)' }}>
                <div style={{ color: '#64748b', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem' }}>Cobertura Estimada</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#2563eb' }}>
                  {results ? `${(results.coverage || 95.2).toFixed(1)}%` : '95.2%'}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#16a34a', marginTop: '0.25rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <TrendingUp size={14} /> Dentro del umbral t_max
                </div>
              </div>

              <div style={{ background: 'white', padding: '1.5rem', borderRadius: '14px', border: '1px solid #e2e8f0', boxShadow: 'var(--shadow-sm)' }}>
                <div style={{ color: '#64748b', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem' }}>Tiempo Medio Estimado</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a' }}>
                  {results ? `${(results.avg_time || 2.4).toFixed(1)} min` : '2.4 min'}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
                  Tráfico: {traffic === 'pico' ? 'Hora pico (1.6x)' : 'Fluido'}
                </div>
              </div>

              <div style={{ background: 'white', padding: '1.5rem', borderRadius: '14px', border: '1px solid #e2e8f0', boxShadow: 'var(--shadow-sm)' }}>
                <div style={{ color: '#64748b', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem' }}>Flota Asignada</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a' }}>
                  {numAmbulances} <span style={{ fontSize: '1rem', color: '#64748b' }}>/ 27</span>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
                  Unidades en servicio
                </div>
              </div>

              <div style={{ background: 'white', padding: '1.5rem', borderRadius: '14px', border: '1px solid #e2e8f0', boxShadow: 'var(--shadow-sm)' }}>
                <div style={{ color: '#64748b', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem' }}>Bases con Unidades</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a' }}>
                  {results ? Object.values(results.allocation).filter((v:any) => v > 0).length : 6} <span style={{ fontSize: '1rem', color: '#64748b' }}>/ {results ? results.base_names.length : 12}</span>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
                  Bases operativas activas
                </div>
              </div>
            </div>

            {/* Distribución por Bases Hospitalarias y Puntos Tácticos */}
            <div style={{ background: 'white', borderRadius: '14px', border: '1px solid #e2e8f0', padding: '1.75rem', marginBottom: '2rem', boxShadow: 'var(--shadow-sm)' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Building2 size={20} color="#2563eb" /> Distribución de Unidades por Base Estratégica (Hospitales y Puntos Tácticos en Vía Pública)
              </h2>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                {results && results.base_names.map((baseName: string, bIdx: number) => {
                  const ambCount = results.allocation[bIdx] || 0;
                  const baseType = results.base_types ? results.base_types[bIdx] : 'Hospital/Clínica';
                  const isTactical = !baseType.toLowerCase().includes('hospital') && !baseType.toLowerCase().includes('clínica') && !baseType.toLowerCase().includes('clinica');

                  return (
                    <div key={bIdx} style={{ padding: '1rem', borderRadius: '10px', background: ambCount > 0 ? '#f0fdf4' : '#f8fafc', border: `1px solid ${ambCount > 0 ? '#bbf7d0' : '#e2e8f0'}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span style={{ 
                            background: isTactical ? '#0f172a' : '#eff6ff', 
                            color: isTactical ? '#38bdf8' : '#1d4ed8', 
                            padding: '2px 6px', 
                            borderRadius: '4px', 
                            fontSize: '0.68rem', 
                            fontWeight: 700 
                          }}>
                            {isTactical ? 'Punto Táctico' : 'Hospital'}
                          </span>
                        </div>
                        <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#0f172a', marginTop: '4px' }}>{baseName}</div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
                          Coord: {results.base_coords[bIdx][0].toFixed(4)}, {results.base_coords[bIdx][1].toFixed(4)}
                        </div>
                      </div>
                      <div style={{ background: ambCount > 0 ? '#16a34a' : '#94a3b8', color: 'white', padding: '0.25rem 0.75rem', borderRadius: '8px', fontWeight: 800, fontSize: '0.85rem' }}>
                        {ambCount} {ambCount === 1 ? 'unidad' : 'unidades'}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Botón de acción */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
              <button 
                onClick={() => setActiveTab('operaciones')}
                style={{ background: '#2563eb', color: 'white', border: 'none', padding: '0.75rem 1.8rem', borderRadius: '10px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                Volver al Mapa de Operaciones <ArrowRight size={18} />
              </button>
            </div>
          </div>
        </div>
      )}

      {renderHowItWorksModal()}
    </div>
  );
}
