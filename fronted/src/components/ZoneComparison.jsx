import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip, Legend
} from 'recharts';
import '../styles/ZoneComparison.css';

const ZoneComparison = () => {
  const [availableZones, setAvailableZones] = useState([]);
  const [selectedZones, setSelectedZones] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAvailableZones();
  }, []);

  const loadAvailableZones = async () => {
    try {
      const scores = await api.getScores();
      const zones = scores.map(s => ({
        code: s.zone_code,
        name: s.zone_name
      }));
      setAvailableZones(zones);
    } catch (err) {
      setError('Error al cargar zonas disponibles');
    }
  };

  const handleZoneSelect = (zoneCode) => {
    if (selectedZones.includes(zoneCode)) {
      setSelectedZones(selectedZones.filter(z => z !== zoneCode));
    } else if (selectedZones.length < 5) {
      setSelectedZones([...selectedZones, zoneCode]);
    }
  };

  const handleCompare = async () => {
    if (selectedZones.length < 2) {
      setError('Selecciona al menos 2 zonas para comparar');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await api.compareZones(selectedZones);
      setComparisonResult(result);
    } catch (err) {
      setError(err.message || 'Error al comparar zonas');
    } finally {
      setLoading(false);
    }
  };

  const handleClearSelection = () => {
    setSelectedZones([]);
    setComparisonResult(null);
  };

  const getOpportunityClass = (level) => {
    if (level === 'Alta') return 'opportunity-high';
    if (level === 'Media') return 'opportunity-medium';
    return 'opportunity-low';
  };

  const getScoreClass = (score) => {
    if (score >= 70) return 'score-high';
    if (score >= 40) return 'score-medium';
    return 'score-low';
  };

  const handleExport = () => {
    if (!comparisonResult) return;

    let csv = 'Métrica,' + comparisonResult.zones.map(z => z.zone_name).join(',') + '\n';

    csv += 'Score,' + comparisonResult.zones.map(z => z.score.toFixed(1)).join(',') + '\n';
    csv += 'Oportunidad,' + comparisonResult.zones.map(z => z.opportunity_level).join(',') + '\n';
    csv += 'Población (contrib),' + comparisonResult.zones.map(z => z.population_contribution.toFixed(1)).join(',') + '\n';
    csv += 'Ingreso (contrib),' + comparisonResult.zones.map(z => z.income_contribution.toFixed(1)).join(',') + '\n';
    csv += 'Educación (contrib),' + comparisonResult.zones.map(z => z.education_contribution.toFixed(1)).join(',') + '\n';
    csv += 'Competencia (penal),' + comparisonResult.zones.map(z => z.competition_penalty.toFixed(1)).join(',') + '\n';

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `comparacion_zonas_${new Date().toISOString().slice(0,10)}.csv`);
    link.click();
  };

  const radarData = comparisonResult?.radar_data || [];
  const zoneColors = ['#006944', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444'];

  return (
    <div className="comparison-container">
      {/* Header */}
      <div className="comparison-header">
        <div>
          <h1 className="comparison-title">Comparación de Zonas</h1>
          <p className="comparison-subtitle">
            Selecciona de 2 a 5 zonas para comparar sus métricas
          </p>
        </div>
        <div className="comparison-actions">
          {comparisonResult && (
            <button className="btn-export" onClick={handleExport}>
              <span className="material-symbols-outlined">download</span>
              Exportar CSV
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="error-message">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}

      {/* Zona de selección */}
      <div className="selection-section">
        <h3>Zonas disponibles</h3>
        <p className="selection-hint">
          Seleccionadas: {selectedZones.length} / 5
        </p>
        <div className="zones-grid">
          {availableZones.map(zone => (
            <div
              key={zone.code}
              className={`zone-chip ${selectedZones.includes(zone.code) ? 'selected' : ''}`}
              onClick={() => handleZoneSelect(zone.code)}
            >
              <span className="zone-code">{zone.code}</span>
              <span className="zone-name">{zone.name}</span>
              {selectedZones.includes(zone.code) && (
                <span className="material-symbols-outlined check-icon">check_circle</span>
              )}
            </div>
          ))}
        </div>
        <div className="selection-actions">
          <button
            className="btn-primary"
            onClick={handleCompare}
            disabled={selectedZones.length < 2 || loading}
          >
            <span className="material-symbols-outlined">compare</span>
            {loading ? 'Comparando...' : 'Comparar Zonas'}
          </button>
          {selectedZones.length > 0 && (
            <button className="btn-outline" onClick={handleClearSelection}>
              Limpiar selección
            </button>
          )}
        </div>
      </div>

      {/* Resultados */}
      {comparisonResult && (
        <div className="results-section">
          {/* Gráfico de Radar */}
          <div className="radar-section">
            <h3>Perfil Comparativo</h3>
            <div className="radar-chart-container">
              <ResponsiveContainer width="100%" height={350}>
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                  <PolarGrid stroke="#e2e8f0" />
                  <PolarAngleAxis
                    dataKey="variable"
                    tick={{ fill: '#64748b', fontSize: 12, fontWeight: 500 }}
                  />
                  <PolarRadiusAxis
                    angle={90}
                    domain={[0, 1]}
                    tick={{ fill: '#94a3b8', fontSize: 10 }}
                    tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                  />
                  {comparisonResult.zones.map((zone, index) => (
                    <Radar
                      key={zone.zone_code}
                      name={zone.zone_name}
                      dataKey={zone.zone_name}
                      stroke={zoneColors[index % zoneColors.length]}
                      fill={zoneColors[index % zoneColors.length]}
                      fillOpacity={0.2}
                      strokeWidth={2}
                    />
                  ))}
                  <Tooltip />
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <p className="radar-note">
              Valores normalizados (0-1). Competencia invertida: más cerca del borde = mejor.
            </p>
          </div>

          {/* Tabla comparativa */}
          <div className="table-section">
            <h3>Tabla Comparativa</h3>
            <div className="table-container">
              <table className="comparison-table">
                <thead>
                  <tr>
                    <th>Métrica</th>
                    {comparisonResult.zones.map(zone => (
                      <th key={zone.zone_code}>{zone.zone_name}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {/* Score */}
                  <tr>
                    <td className="metric-label">Score</td>
                    {comparisonResult.zones.map(zone => {
                      const isBest = zone.score === comparisonResult.best_values.score.value;
                      return (
                        <td
                          key={zone.zone_code}
                          className={`${isBest ? 'best-value' : ''} ${getScoreClass(zone.score)}`}
                        >
                          {zone.score.toFixed(1)}
                        </td>
                      );
                    })}
                  </tr>
                  {/* Oportunidad */}
                  <tr>
                    <td className="metric-label">Oportunidad</td>
                    {comparisonResult.zones.map(zone => (
                      <td key={zone.zone_code}>
                        <span className={`opportunity-badge ${getOpportunityClass(zone.opportunity_level)}`}>
                          {zone.opportunity_level}
                        </span>
                      </td>
                    ))}
                  </tr>
                  {/* Población */}
                  <tr>
                    <td className="metric-label">Población (contribución)</td>
                    {comparisonResult.zones.map(zone => {
                      const isBest = zone.population_contribution === comparisonResult.best_values.population.value;
                      return (
                        <td key={zone.zone_code} className={isBest ? 'best-value positive' : 'positive'}>
                          +{zone.population_contribution.toFixed(1)}
                        </td>
                      );
                    })}
                  </tr>
                  {/* Ingreso */}
                  <tr>
                    <td className="metric-label">Ingreso (contribución)</td>
                    {comparisonResult.zones.map(zone => {
                      const isBest = zone.income_contribution === comparisonResult.best_values.income.value;
                      return (
                        <td key={zone.zone_code} className={isBest ? 'best-value positive' : 'positive'}>
                          +{zone.income_contribution.toFixed(1)}
                        </td>
                      );
                    })}
                  </tr>
                  {/* Educación */}
                  <tr>
                    <td className="metric-label">Educación (contribución)</td>
                    {comparisonResult.zones.map(zone => {
                      const isBest = zone.education_contribution === comparisonResult.best_values.education.value;
                      return (
                        <td key={zone.zone_code} className={isBest ? 'best-value positive' : 'positive'}>
                          +{zone.education_contribution.toFixed(1)}
                        </td>
                      );
                    })}
                  </tr>
                  {/* Competencia */}
                  <tr>
                    <td className="metric-label">Competencia (penalización)</td>
                    {comparisonResult.zones.map(zone => {
                      const isBest = zone.competition_penalty === comparisonResult.best_values.competition.value;
                      return (
                        <td key={zone.zone_code} className={isBest ? 'best-value negative' : 'negative'}>
                          -{zone.competition_penalty.toFixed(1)}
                        </td>
                      );
                    })}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Resumen de mejores valores */}
          <div className="best-summary">
            <h3>Mejores valores por métrica</h3>
            <div className="best-grid">
              <div className="best-card">
                <span className="best-label">Mejor Score</span>
                <span className="best-zone">{comparisonResult.best_values.score.zone}</span>
                <span className="best-value">{comparisonResult.best_values.score.value.toFixed(1)}</span>
              </div>
              <div className="best-card">
                <span className="best-label">Mayor Población</span>
                <span className="best-zone">{comparisonResult.best_values.population.zone}</span>
                <span className="best-value">+{comparisonResult.best_values.population.value.toFixed(1)}</span>
              </div>
              <div className="best-card">
                <span className="best-label">Mayor Ingreso</span>
                <span className="best-zone">{comparisonResult.best_values.income.zone}</span>
                <span className="best-value">+{comparisonResult.best_values.income.value.toFixed(1)}</span>
              </div>
              <div className="best-card">
                <span className="best-label">Mayor Educación</span>
                <span className="best-zone">{comparisonResult.best_values.education.zone}</span>
                <span className="best-value">+{comparisonResult.best_values.education.value.toFixed(1)}</span>
              </div>
              <div className="best-card">
                <span className="best-label">Menor Competencia</span>
                <span className="best-zone">{comparisonResult.best_values.competition.zone}</span>
                <span className="best-value">-{comparisonResult.best_values.competition.value.toFixed(1)}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ZoneComparison;