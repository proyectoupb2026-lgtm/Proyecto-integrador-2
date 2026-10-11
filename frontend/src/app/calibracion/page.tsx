"use client";

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Save, Activity, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { API_BASE_URL } from '../../config/api';

const DynamicCalibracionMap = dynamic(() => import('../../components/CalibracionMap'), {
  ssr: false,
  loading: () => <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Cargando mapa de calibración...</div>
});

export default function Calibracion() {
  const [activeMode, setActiveMode] = useState<'zonas' | 'bases'>('zonas');
  const [zones, setZones] = useState<any[]>([]);
  const [bases, setBases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showList, setShowList] = useState(true);

  const loadData = () => {
    setLoading(true);
    if (activeMode === 'zonas') {
      fetch(`${API_BASE_URL}/api/zonas`)
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            const z = data.node_coords.map((c: any, i: number) => ({
              id: data.node_ids ? data.node_ids[i] : `ZC_${String(i+1).padStart(2, '0')}`,
              idx: i,
              name: data.node_names[i],
              lat: c[0],
              lon: c[1],
              street: 'Ubicación actual'
            }));
            setZones(z);
          }
          setLoading(false);
        })
        .catch(() => setLoading(false));
    } else {
      fetch(`${API_BASE_URL}/api/bases`)
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            const b = data.base_coords.map((c: any, i: number) => ({
              id: `BASE_${i+1}`,
              idx: i,
              name: data.base_names[i],
              tipo: data.base_types ? data.base_types[i] : 'Punto Táctico',
              lat: c[0],
              lon: c[1],
              street: 'Ubicación actual'
            }));
            setBases(b);
          }
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }
  };

  useEffect(() => {
    loadData();
  }, [activeMode]);

  const currentItems = activeMode === 'zonas' ? zones : bases;

  const handleSnap = (idx: number, lat: number, lon: number, street: string) => {
    if (activeMode === 'zonas') {
      setZones(prev => prev.map(z => z.idx === idx ? { ...z, lat, lon, street } : z));
    } else {
      setBases(prev => prev.map(b => b.idx === idx ? { ...b, lat, lon, street } : b));
    }
  };

  const handleRename = (idx: number, newName: string) => {
    if (activeMode === 'zonas') {
      setZones(prev => prev.map(z => z.idx === idx ? { ...z, name: newName } : z));
    } else {
      setBases(prev => prev.map(b => b.idx === idx ? { ...b, name: newName } : b));
    }
  };

  const handleDelete = (idx: number) => {
    if (activeMode === 'zonas') {
      setZones(prev => prev.filter(z => z.idx !== idx));
    } else {
      setBases(prev => prev.filter(b => b.idx !== idx));
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (activeMode === 'zonas') {
        const payload = {
          zones: zones.map(z => ({ id: z.id, name: z.name, lat: z.lat, lon: z.lon }))
        };
        const res = await fetch(`${API_BASE_URL}/api/zonas/save`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
          alert(`¡Zonas de demanda guardadas con éxito!\nTotal zonas actualizadas: ${data.total_zonas || zones.length}.\nSe actualizó la bitácora.`);
        } else {
          alert('Error: ' + data.detail);
        }
      } else {
        const payload = {
          bases: bases.map(b => ({ name: b.name, lat: b.lat, lon: b.lon, tipo: b.tipo }))
        };
        const res = await fetch(`${API_BASE_URL}/api/bases/save`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
          alert(`¡Bases y Puntos Tácticos guardados con éxito!\nTotal bases calibradas: ${data.total_bases || bases.length}.\nEl modelo matemático cargará estas nuevas coordenadas.`);
        } else {
          alert('Error: ' + data.detail);
        }
      }
    } catch (e) {
      alert('Error guardando la calibración');
    }
    setSaving(false);
  };

  const handleAddZone = () => {
    if (activeMode === 'zonas') {
      const name = prompt("Escribe el nombre de la nueva zona de demanda (ej: Barrio Pasatiempo / Calle 24):");
      if (!name || name.trim() === '') return;
      
      const newIdx = zones.length > 0 ? Math.max(...zones.map(z => z.idx)) + 1 : 0;
      const newId = `ZC_${String(newIdx + 1).padStart(2, '0')}`;
      const newZone = {
        id: newId,
        idx: newIdx,
        name: name.trim(),
        lat: 8.7530,
        lon: -75.8820,
        street: 'Arrastra el marcador a la vía deseada'
      };
      setZones([...zones, newZone]);
    } else {
      const name = prompt("Escribe el nombre de la nueva base táctica (ej: Punto Táctico El Dorado):");
      if (!name || name.trim() === '') return;
      
      const newIdx = bases.length > 0 ? Math.max(...bases.map(b => b.idx)) + 1 : 0;
      const newBase = {
        id: `BASE_${newIdx + 1}`,
        idx: newIdx,
        name: name.trim(),
        tipo: 'Punto Táctico',
        lat: 8.7530,
        lon: -75.8820,
        street: 'Arrastra el marcador a la vía deseada'
      };
      setBases([...bases, newBase]);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#f8fafc' }}>
      <header style={{ padding: '0.875rem 2rem', background: 'white', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none', color: 'var(--color-text-main)', fontWeight: 600 }}>
            <ArrowLeft size={20} /> Volver a Operaciones
          </Link>
          <div style={{ height: '24px', width: '1px', background: 'var(--color-border)' }}></div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <button
              onClick={() => setActiveMode('zonas')}
              style={{
                background: activeMode === 'zonas' ? '#ea580c' : '#f1f5f9',
                color: activeMode === 'zonas' ? 'white' : '#475569',
                border: 'none',
                padding: '0.45rem 0.85rem',
                borderRadius: '6px',
                fontWeight: 700,
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              Zonas de Demanda ({zones.length})
            </button>
            <button
              onClick={() => setActiveMode('bases')}
              style={{
                background: activeMode === 'bases' ? '#059669' : '#f1f5f9',
                color: activeMode === 'bases' ? 'white' : '#475569',
                border: 'none',
                padding: '0.45rem 0.85rem',
                borderRadius: '6px',
                fontWeight: 700,
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              Bases y Puntos Tácticos ({bases.length})
            </button>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button 
            onClick={() => setShowList(!showList)}
            style={{ background: '#f8fafc', color: '#334155', border: '1px solid #cbd5e1', padding: '0.65rem 1rem', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}
          >
            {showList ? 'Ocultar Lista' : 'Ver Lista'}
          </button>
          <button 
            onClick={handleAddZone}
            disabled={saving || loading}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#eff6ff', color: '#1d4ed8', border: '1px solid #bfdbfe', padding: '0.65rem 1.25rem', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}
          >
            + {activeMode === 'zonas' ? 'Nueva Zona' : 'Nuevo Punto Táctico'}
          </button>
          <button 
            onClick={handleSave} 
            disabled={saving || loading}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: activeMode === 'zonas' ? '#ea580c' : '#059669', color: 'white', border: 'none', padding: '0.65rem 1.5rem', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', opacity: saving ? 0.7 : 1 }}
          >
            <Save size={18} /> {saving ? 'Guardando...' : `Guardar ${activeMode === 'zonas' ? 'Zonas' : 'Bases'}`}
          </button>
        </div>
      </header>

      <div style={{ flex: 1, display: 'flex', position: 'relative', overflow: 'hidden' }}>
        {/* Panel lateral con la lista */}
        {showList && (
          <aside style={{ width: '340px', background: 'white', borderRight: '1px solid var(--color-border)', display: 'flex', flexDirection: 'column', zIndex: 10 }}>
            <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--color-border)', fontWeight: 700, fontSize: '0.95rem', color: '#334155' }}>
              {activeMode === 'zonas' ? 'Zonas de Demanda Vial' : 'Bases y Puntos Tácticos'} ({currentItems.length})
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: '0.75rem' }}>
              {currentItems.map((item) => (
                <div key={item.idx} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.75rem', marginBottom: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#0f172a' }}>{item.name}</div>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <button 
                        onClick={() => {
                          const n = prompt('Nuevo nombre:', item.name);
                          if (n && n.trim() !== '') handleRename(item.idx, n.trim());
                        }}
                        title="Cambiar nombre"
                        style={{ background: 'white', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer', padding: '2px 6px', fontSize: '11px', fontWeight: 600, color: '#475569' }}
                      >
                        Editar
                      </button>
                      <button 
                        onClick={() => {
                          if (confirm(`¿Eliminar "${item.name}"?`)) handleDelete(item.idx);
                        }}
                        title="Eliminar"
                        style={{ background: '#fee2e2', border: '1px solid #fca5a5', color: '#b91c1c', borderRadius: '4px', cursor: 'pointer', padding: '2px 6px', fontSize: '11px', fontWeight: 600 }}
                      >
                        Eliminar
                      </button>
                    </div>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
                    <b>Coord:</b> {item.lat.toFixed(5)}, {item.lon.toFixed(5)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: activeMode === 'zonas' ? '#ea580c' : '#059669', marginTop: '2px' }}>
                    {item.street || 'En mapa'}
                  </div>
                </div>
              ))}
            </div>
          </aside>
        )}

        {/* Mapa */}
        <div style={{ flex: 1, position: 'relative' }}>
          {!loading && (
            <DynamicCalibracionMap 
              zones={currentItems} 
              onSnap={handleSnap} 
              onRename={handleRename} 
              onDelete={handleDelete} 
            />
          )}
          {loading && <div style={{ padding: '2rem', textAlign: 'center' }}>Cargando datos...</div>}
        </div>
      </div>
    </div>
  );
}
