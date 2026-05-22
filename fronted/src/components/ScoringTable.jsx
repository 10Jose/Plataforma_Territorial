import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import '../styles/ScoringTable.css';
import StatsSummary from './StatsSummary';
import RadarChartComponent from './RadarChart';
import '../styles/Tooltip.css';

const ScoringTable = () => {
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [loadingIA, setLoadingIA] = useState(false);
  const [error, setError] = useState(null);
  const [selectedZone, setSelectedZone] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const [combinedScores, setCombinedScores] = useState({});
  const [iaCalculated, setIaCalculated] = useState(false);
  const [combinedStats, setCombinedStats] = useState(null);
  const [iaMessage, setIaMessage] = useState(null);

  const downloadCSV = (csv, filename) => {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

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

  const loadCombinedStats = async () => {
    try {
      const stats = await api.getCombinedStats();
      setCombinedStats(stats);
    } catch (err) {
      // Silencioso
    }
  };

  const loadCombinedScores = useCallback(async () => {
    setLoadingIA(true);
    setIaMessage(null);
    try {
      const combined = {};
      let hasAnyPrediction = false;

      for (const zone of scores) {
        try {
          const combinedData = await api.getCombinedAnalysis(zone.zone_code);
          if (combinedData && combinedData.score_combinado_ia !== undefined) {
            combined[zone.zone_code] = combinedData;
            hasAnyPrediction = true;
          }
        } catch (err) {
          // Silencioso
        }
      }

      if (!hasAnyPrediction) {
        setIaMessage({
          type: 'info',
          text: 'No es posible calcular el Score Combinado IA en este momento.',
          suggestion: 'Para desbloquear esta funcionalidad, primero debes generar datos potenciales. Dirígete a la pestaña "Predicción" y haz clic en "Predecir Todas". Una vez completado, regresa aquí y vuelve a intentarlo.'
        });
        setCombinedScores({});
        setIaCalculated(false);
      } else {
        setCombinedScores(combined);
        setIaCalculated(true);
        sessionStorage.setItem('combinedScores', JSON.stringify(combined));
        sessionStorage.setItem('iaCalculated', 'true');
        await loadCombinedStats();
      }
    } catch (err) {
      // Silencioso
    } finally {
      setLoadingIA(false);
    }
  }, [scores]);

  useEffect(() => {
    loadScores();
    const savedCombined = sessionStorage.getItem('combinedScores');
    const savedIaCalculated = sessionStorage.getItem('iaCalculated');
    if (savedCombined) {
      setCombinedScores(JSON.parse(savedCombined));
      setIaCalculated(savedIaCalculated === 'true');
      loadCombinedStats();
    }
  }, []);

  const handleCalculateScoring = async () => {
    setCalculating(true);
    setError(null);
    try {
      await api.calculateScoring();
      await new Promise(resolve => setTimeout(resolve, 1000));
      await loadScores();
      setCombinedScores({});
      setIaCalculated(false);
      setCombinedStats(null);
      setIaMessage(null);
      sessionStorage.removeItem('combinedScores');
      sessionStorage.removeItem('iaCalculated');
    } catch (err) {
      setError(err.message || 'Error al calcular scoring');
    } finally {
      setCalculating(false);
    }
  };

  const handleExportScores = () => {
    if (!scores.length) {
        setError('No hay datos para exportar. Calcula el scoring primero.');
        return;
        }

    let csv = 'Zona,Score Real,Oportunidad,Población,Ingreso,Educación,Competencia,Score Combinado IA,Predicción ML\n';

    scores.forEach(item => {
      const combined = combinedScores[item.zone_code];
      csv += `${item.zone_name},${item.score.toFixed(1)},${item.opportunity_level},`;
      csv += `+${item.contributions?.population || 0},+${item.contributions?.income || 0},`;
      csv += `+${item.contributions?.education || 0},-${item.contributions?.competition_penalty || 0},`;
      csv += `${combined?.score_combinado_ia?.toFixed(1) || 'N/A'},${combined?.prediction_ml?.toFixed(1) || 'N/A'}\n`;
    });

    downloadCSV(csv, `scores_${new Date().toISOString().slice(0, 10)}.csv`);
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
        <div className="scoring-header-buttons">
          <button
            className="btn-export"
            onClick={handleExportScores}
            disabled={scores.length === 0}
          >
            <span className="material-symbols-outlined">download</span>
            Exportar CSV
          </button>
          <button
            className="btn-calculate-ia"
            onClick={loadCombinedScores}
            disabled={loadingIA || scores.length === 0}
          >
            <span className="material-symbols-outlined">auto_awesome</span>
            {loadingIA ? 'Calculando IA...' : 'Calcular Score IA'}
          </button>
          <button
            className="btn-calculate"
            onClick={handleCalculateScoring}
            disabled={calculating}
          >
            <span className="material-symbols-outlined">calculate</span>
            {calculating ? 'Calculando...' : 'Calcular Scoring'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}

      {/* Mensaje IA */}
      {iaMessage && (
        <div className="ia-message-card">
          <div className="ia-message-header">
            <span className="material-symbols-outlined">psychology</span>
            <span>Asistente IA</span>
          </div>
          <div className="ia-message-body">
            <p className="ia-message-text">{iaMessage.text}</p>
            <div className="ia-message-suggestion">
              <span className="material-symbols-outlined">lightbulb</span>
              <p>{iaMessage.suggestion}</p>
            </div>
          </div>
          <button className="ia-message-close" onClick={() => setIaMessage(null)}>
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
      )}

      {scores.length > 0 && <StatsSummary scores={scores} />}

      {combinedStats && combinedStats.zones_with_ia > 0 && (
        <div className="ia-stats-bar">
          <div className="ia-stat-item">
            <span className="ia-stat-label">Zonas con IA</span>
            <span className="ia-stat-value">{combinedStats.zones_with_ia}/{combinedStats.total_zones}</span>
          </div>
          <div className="ia-stat-item">
            <span className="ia-stat-label">Mejoraron</span>
            <span className="ia-stat-value improved">{combinedStats.classification_changes?.improved || 0}</span>
          </div>
          <div className="ia-stat-item">
            <span className="ia-stat-label">Confianza Promedio</span>
            <span className={`ia-stat-value confidence-${combinedStats.average_confidence?.toLowerCase()}`}>
              {combinedStats.average_confidence}
            </span>
          </div>
        </div>
      )}

      {!iaCalculated && scores.length > 0 && !iaMessage && (
        <div className="ia-hint-bar">
          <span className="material-symbols-outlined">auto_awesome</span>
          <span>Haz clic en "Calcular Score IA" para obtener el Score Combinado que integra el Score Real con la Predicción ML.</span>
        </div>
      )}

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
                  <th className="text-right">Población</th>
                  <th className="text-right">Ingreso</th>
                  <th className="text-right">Educación</th>
                  <th className="text-right">Competencia</th>
                  <th className="text-right">Score Real</th>
                  <th className="text-center">Oportunidad</th>
                  <th className="text-right">Score Combinado IA</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {paginatedScores.map((item, index) => (
                  <tr key={item.id}>
                    <td className="rank">{startIndex + index + 1}</td>
                    <td className="zone-name">{item.zone_name}</td>
                    <td className="text-right contribution-cell"><span className="contribution-value" style={{ fontSize: '0.99rem' }}>+{item.contributions?.population || 0}</span></td>
                    <td className="text-right contribution-cell"><span className="contribution-value" style={{ fontSize: '0.99rem' }}>+{item.contributions?.income || 0}</span></td>
                    <td className="text-right contribution-cell"><span className="contribution-value" style={{ fontSize: '0.99rem' }}>+{item.contributions?.education || 0}</span></td>
                    <td className="text-right contribution-cell penalty"><span className="contribution-value" style={{ fontSize: '1.10rem' }}>-{item.contributions?.competition_penalty || 0}</span></td>
                    <td className="text-right"><span className={`score-value ${getScoreClass(item.score)}`} style={{ fontSize: '1.10rem', fontWeight: 600 }}>{item.score.toFixed(1)}</span></td>
                    <td className="text-center"><span className={`opportunity-badge ${getOpportunityClass(item.opportunity_level)}`}>{item.opportunity_level}</span></td>
                    <td className="text-right">
                      {combinedScores[item.zone_code] ? (
                        <span className={`score-value ${getScoreClass(combinedScores[item.zone_code].score_combinado_ia)}`} style={{ fontSize: '1.10rem' }}>
                          {combinedScores[item.zone_code].score_combinado_ia?.toFixed(1)}
                        </span>
                      ) : (
                        <span
                          className="ia-pending"
                          style={{
                            color: '#94a3b8',
                            fontSize: '0.8rem',
                            cursor: 'help',
                            borderBottom: '1px dashed #94a3b8'
                          }}
                          title="Para obtener el Score Combinado IA: Ve a Predicción → Predecir Todas, luego vuelve aquí y haz clic en Calcular Score IA"
                        >
                          Pendiente
                        </span>
                      )}
                    </td>
                    <td className="text-center"><button className="btn-detail" onClick={() => setSelectedZone(item)} title="Ver detalle"><span className="material-symbols-outlined">visibility</span></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} className="pagination-btn"><span className="material-symbols-outlined">chevron_left</span></button>
              <span className="pagination-info">Página {currentPage} de {totalPages}</span>
              <button onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages} className="pagination-btn"><span className="material-symbols-outlined">chevron_right</span></button>
            </div>
          )}
        </>
      )}

      {selectedZone && (
        <div className="modal-overlay" onClick={() => setSelectedZone(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header"><h2>{selectedZone.zone_name}</h2><button className="modal-close" onClick={() => setSelectedZone(null)}><span className="material-symbols-outlined">close</span></button></div>
            <div className="modal-body">
              <RadarChartComponent data={selectedZone} zoneName={selectedZone.zone_name} />
              <div className="detail-score"><span className="detail-label">Score Real</span><span className={`detail-value ${getScoreClass(selectedZone.score)}`}>{selectedZone.score.toFixed(1)}</span></div>
              {combinedScores[selectedZone.zone_code] && (
                <div className="detail-score"><span className="detail-label">Score Combinado IA</span><span className={`detail-value ${getScoreClass(combinedScores[selectedZone.zone_code].score_combinado_ia)}`}>{combinedScores[selectedZone.zone_code].score_combinado_ia?.toFixed(1)}</span></div>
              )}
              <div className="detail-opportunity"><span className="detail-label">Oportunidad</span><span className={`opportunity-badge ${getOpportunityClass(selectedZone.opportunity_level)}`}>{selectedZone.opportunity_level}</span></div>
              {combinedScores[selectedZone.zone_code] && (
                <div className="combined-info">
                  <p className="combined-formula">📐 Fórmula: Score_Combinado_IA = (Score_Real × 0.6) + (Predicción_ML × 0.4)</p>
                  <p className="combined-detail">Score Real: {combinedScores[selectedZone.zone_code].score_real?.toFixed(1)} × 0.6 = {(combinedScores[selectedZone.zone_code].score_real * 0.6)?.toFixed(1)}</p>
                  <p className="combined-detail">Predicción ML: {combinedScores[selectedZone.zone_code].prediction_ml?.toFixed(1)} × 0.4 = {(combinedScores[selectedZone.zone_code].prediction_ml * 0.4)?.toFixed(1)}</p>
                  <p className="combined-detail">✅ Score Combinado IA: <strong>{combinedScores[selectedZone.zone_code].score_combinado_ia?.toFixed(1)}</strong></p>
                  <p className="combined-confidence">Confianza: {combinedScores[selectedZone.zone_code].confidence || 'N/A'}</p>
                </div>
              )}
              <h3>Contribuciones</h3>
              <div className="contributions-list">
                <div className="contribution-item positive"><span>Población</span><span className="value">+{selectedZone.contributions?.population || 0}</span></div>
                <div className="contribution-item positive"><span>Ingreso</span><span className="value">+{selectedZone.contributions?.income || 0}</span></div>
                <div className="contribution-item positive"><span>Educación</span><span className="value">+{selectedZone.contributions?.education || 0}</span></div>
                <div className="contribution-item negative"><span>Competencia (penalización)</span><span className="value">-{selectedZone.contributions?.competition_penalty || 0}</span></div>
              </div>
              <h3>Pesos Utilizados</h3>
              <div className="weights-list">
                {selectedZone.weights_used && Object.entries(selectedZone.weights_used).map(([key, value]) => (
                  <div key={key} className="weight-item"><span>{key}</span><span>{value}%</span></div>
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