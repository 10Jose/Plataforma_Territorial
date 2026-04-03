import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const ZonesList = ({ refreshTrigger }) => {
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchZones = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getZones(0, 100);
      setZones(data.zones || []);
    } catch (err) {
      console.error('Error fetching zones:', err);
      setError(err.message || 'Error al cargar zonas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchZones();
  }, [refreshTrigger]);

  if (loading) return <div style={{ padding: '1rem', textAlign: 'center' }}>Cargando zonas...</div>;
  if (error) return <div style={{ padding: '1rem', color: '#9e3f4e', backgroundColor: '#ff8b9a20', borderRadius: '0.75rem' }}>Error: {error}</div>;

  return (
    <div style={{ marginTop: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3>📌 Zonas disponibles</h3>
        <button onClick={fetchZones} disabled={loading} style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem', background: '#0d9488', color: 'white', border: 'none', borderRadius: '0.5rem', cursor: 'pointer' }}>
          {loading ? 'Cargando...' : '🔄 Actualizar'}
        </button>
      </div>
      {zones.length === 0 ? (
        <p>No hay zonas disponibles. Carga un archivo CSV válido.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {zones.map((zone, idx) => (
            <li key={idx} style={{ padding: '0.5rem', borderBottom: '1px solid #e1e9ee' }}>
              <strong>{zone.name}</strong>
              {zone.code && <span style={{ color: '#566166', marginLeft: '0.5rem' }}>({zone.code})</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ZonesList;