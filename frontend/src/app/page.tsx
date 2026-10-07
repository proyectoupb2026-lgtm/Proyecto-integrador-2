"use client";

import React, { useState } from 'react';
import dynamic from 'next/dynamic';

const DynamicMap = dynamic(() => import('../components/Map'), {
  ssr: false,
  loading: () => <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Cargando mapa...</div>
});

export default function Home() {
  const [numAmbulances, setNumAmbulances] = useState(6);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleRunModel = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          num_ambulances: numAmbulances,
          num_nodes: 13,
          num_bases: 7,
          t_max: 10.0,
          alpha: 0.5
        })
      });
      const data = await response.json();
      if (data.status === "success") {
        setResults(data);
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

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <span style={{ fontSize: '1.5rem' }}>🚑</span>
          <h1>APH Montería</h1>
        </div>
        <div className="sidebar-content">
          <h2 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--color-text-muted)' }}>Configuración</h2>
          
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
              Flota Total de Ambulancias
            </label>
            <input 
              type="range" 
              min="1" 
              max="15" 
              value={numAmbulances} 
              onChange={e => setNumAmbulances(parseInt(e.target.value))} 
              style={{ width: '100%' }} 
            />
            <div style={{ textAlign: 'center', marginTop: '0.5rem', fontWeight: 600 }}>
              {numAmbulances} Vehículos
            </div>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
              Modelo Matemático
            </label>
            <select style={{ width: '100%', padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <option>Optimización MILP</option>
              <option disabled>Simulación SimPy (Próximamente)</option>
            </select>
          </div>

          <button className="btn-primary" onClick={handleRunModel} disabled={loading}>
            {loading ? 'Calculando MILP...' : 'Ejecutar Modelo'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="topbar">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Panel de Control Operativo</h2>
        </header>
        
        {/* Mapa interactivo */}
        <div className="map-container">
          <DynamicMap results={results} />
          
          {/* Tarjetas KPI flotantes */}
          {results && (
            <div style={{ position: 'absolute', top: '1rem', right: '1rem', display: 'flex', gap: '1rem', zIndex: 1000 }}>
              <div className="kpi-card" style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Ambulancias Asignadas</p>
                <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-primary)' }}>
                  {Object.values(results.allocation).reduce((a: any, b: any) => a + b, 0)}
                </p>
              </div>
              <div className="kpi-card" style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Bases Activas</p>
                <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-accent)' }}>
                  {Object.values(results.allocation).filter((v: any) => v > 0).length}
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
