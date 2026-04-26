import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import '../styles/ScoringTable.css';
import StatsSummary from './StatsSummary';
import RadarChartComponent from './RadarChart';
import '../styles/Tooltip.css';

const ScoringTable = () => {
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [error, setError] = useState(null);
  const [selectedZone, setSelectedZone] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    loadScores();
  }, []);

  const loadScores = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getScores();
      setScores(data || []);
    } catch (err) {
      setError(err.message || 'Error al cargar scores');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculateScoring = async () => {
    setCalculating(true);
    setError(null);
    try {
      await api.calculateScoring();
      await new Promise(resolve => setTimeout(resolve, 500));
      await loadScores();
    } catch (err) {
      setError(err.message || 'Error al calcular scoring');
    } finally {
      setCalculating(false);
    }
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

  // Paginación
  const totalPages = Math.ceil(scores.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedScores = scores.slice(startIndex, startIndex + itemsPerPage);

  if (loading) {
    return (
      <div className="scoring-loading">
        <div className="spinner-large"></div>
        <p>Cargando scoring...</p>
      </div>
    );
  }

  return (
    <div className="scoring-container">
      {/* Header */}
      <div className="scoring-header">
        <div>
          <h1 className="scoring-title">
            Análisis de Resultados
            <span className="tooltip-wrapper">
              <span className="material-symbols-outlined tooltip-icon">help</span>
              <span className="tooltip-content">
                Visión unificada del scoring territorial.<br/>
                Los scores se calculan usando los pesos configurados en "Configuración".
              </span>
            </span>
          </h1>
          <p className="scoring-subtitle">
            Visión unificada del desempeño territorial por zonas de oportunidad.
          </p>
        </div>
        <button
          className="btn-calculate"
          onClick={handleCalculateScoring}
          disabled={calculating}
        >
          <span className="material-symbols-outlined">calculate</span>
          {calculating ? 'Calculando...' : 'Calcular Scoring'}
          <span className="tooltip-wrapper">
            <span className="material-symbols-outlined tooltip-icon" style={{ color: 'white', opacity: 0.8 }}>help</span>
            <span className="tooltip-content">
              Ejecuta el cálculo de scoring para todas las zonas.<br/>
              Usa los pesos del perfil activo en Configuración.
            </span>
          </span>
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="error-message">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}

      {/* Stats Summary */}
      {scores.length > 0 && <StatsSummary scores={scores} />}

      {/* Tabla de Scores */}
      {scores.length === 0 ? (
        <div className="empty-state">
          <span className="material-symbols-outlined">analytics</span>
          <h3>No hay scores calculados</h3>
          <p>Haz clic en "Calcular Scoring" para evaluar las zonas</p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="scoring-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Zona</th>
                  <th className="text-right">
                    Población
                    <span className="tooltip-wrapper">
                      <span className="material-symbols-outlined tooltip-icon">help</span>
                      <span className="tooltip-content">
                        Contribución de la variable Población al Score final.<br/>
                        Fórmula: Población × Peso_Población
                      </span>
                    </span>
                  </th>
                  <th className="text-right">
                    Ingreso
                    <span className="tooltip-wrapper">
                      <span className="material-symbols-outlined tooltip-icon">help</span>
                      <span className="tooltip-content">
                        Contribución de la variable Ingreso al Score final.<br/>
                        Fórmula: Ingreso × Peso_Ingreso
                      </span>
                    </span>
                  </th>
                  <th className="text-right">
                    Educación
                    <span className="tooltip-wrapper">
                      <span className="material-symbols-outlined tooltip-icon">help</span>
                      <span className="tooltip-content">
                        Contribución de la variable Educación al Score final.<br/>
                        Fórmula: Educación × Peso_Educación
                      </span>
                    </span>
                  </th>
                  <th className="text-right">
                    Competencia
                    <span className="tooltip-wrapper">
                      <span className="material-symbols-outlined tooltip-icon">help</span>
                      <span className="tooltip-content">
                        Penalización por competencia. Reduce el Score final.<br/>
                        Fórmula: Competencia × Peso_Competencia
                      </span>
                    </span>
                  </th>
                  <th className="text-right">
                    Score
                    <span className="tooltip-wrapper">
                      <span className="material-symbols-outlined tooltip-icon">help</span>
                      <span className="tooltip-content">
                        Score calculado con fórmula ponderada:<br/>
                        (Pob × w1) + (Ing × w2) + (Edu × w3) - (Comp × w4)
                      </span>
                    </span>
                  </th>
                  <th className="text-center">
                    Oportunidad
                    <span className="tooltip-wrapper">
                      <span className="material-symbols-outlined tooltip-icon">help</span>
                      <span className="tooltip-content">
                        Clasificación según el Score:<br/>
                        Alta: ≥70 | Media: 40-69 | Baja: &lt;40
                      </span>
                    </span>
                  </th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {paginatedScores.map((item, index) => (
                  <tr key={item.id}>
                    <td className="rank">{startIndex + index + 1}</td>
                    <td className="zone-name">{item.zone_name}</td>
                    <td className="text-right contribution-cell">
                      <span className="contribution-value">+{item.contributions?.population || 0}</span>
                    </td>
                    <td className="text-right contribution-cell">
                      <span className="contribution-value">+{item.contributions?.income || 0}</span>
                    </td>
                    <td className="text-right contribution-cell">
                      <span className="contribution-value">+{item.contributions?.education || 0}</span>
                    </td>
                    <td className="text-right contribution-cell penalty">
                      <span className="contribution-value">-{item.contributions?.competition_penalty || 0}</span>
                    </td>
                    <td className="text-right">
                      <span className={`score-value ${getScoreClass(item.score)}`}>
                        {item.score.toFixed(1)}
                      </span>
                    </td>
                    <td className="text-center">
                      <span className={`opportunity-badge ${getOpportunityClass(item.opportunity_level)}`}>
                        {item.opportunity_level}
                      </span>
                    </td>
                    <td className="text-center">
                      <button
                        className="btn-detail"
                        onClick={() => setSelectedZone(item)}
                        title="Ver detalle"
                      >
                        <span className="material-symbols-outlined">visibility</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Paginación */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="pagination-btn"
              >
                <span className="material-symbols-outlined">chevron_left</span>
              </button>
              <span className="pagination-info">
                Página {currentPage} de {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="pagination-btn"
              >
                <span className="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          )}
        </>
      )}

      {/* Modal de Detalle */}
      {selectedZone && (
        <div className="modal-overlay" onClick={() => setSelectedZone(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedZone.zone_name}</h2>
              <button className="modal-close" onClick={() => setSelectedZone(null)}>
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <div className="modal-body">
              <RadarChartComponent
                data={selectedZone}
                zoneName={selectedZone.zone_name}
              />
              <div className="detail-score">
                <span className="detail-label">Score Final</span>
                <span className={`detail-value ${getScoreClass(selectedZone.score)}`}>
                  {selectedZone.score.toFixed(1)}
                </span>
              </div>
              <div className="detail-opportunity">
                <span className="detail-label">Oportunidad</span>
                <span className={`opportunity-badge ${getOpportunityClass(selectedZone.opportunity_level)}`}>
                  {selectedZone.opportunity_level}
                </span>
              </div>

              <h3>Contribuciones</h3>
              <div className="contributions-list">
                <div className="contribution-item positive">
                  <span>Población</span>
                  <span className="value">+{selectedZone.contributions?.population || 0}</span>
                </div>
                <div className="contribution-item positive">
                  <span>Ingreso</span>
                  <span className="value">+{selectedZone.contributions?.income || 0}</span>
                </div>
                <div className="contribution-item positive">
                  <span>Educación</span>
                  <span className="value">+{selectedZone.contributions?.education || 0}</span>
                </div>
                <div className="contribution-item negative">
                  <span>Competencia (penalización)</span>
                  <span className="value">-{selectedZone.contributions?.competition_penalty || 0}</span>
                </div>
              </div>

              <h3>Pesos Utilizados</h3>
              <div className="weights-list">
                {selectedZone.weights_used && Object.entries(selectedZone.weights_used).map(([key, value]) => (
                  <div key={key} className="weight-item">
                    <span>{key}</span>
                    <span>{value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScoringTable;