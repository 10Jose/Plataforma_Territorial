import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import '../styles/RecommendationsPanel.css';

const RecommendationsPanel = () => {
  const [zones, setZones] = useState([]);
  const [selectedZone, setSelectedZone] = useState('');
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadZones();
  }, []);

  const loadZones = async () => {
    try {
      const data = await api.getScores();
      setZones(data || []);
    } catch (err) {
      // Silencioso
    }
  };

  const handleGetRecommendations = async () => {
    if (!selectedZone) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getZoneRecommendations(selectedZone);
      setRecommendations(data);
    } catch (err) {
      setError(err.message || 'Error al obtener recomendaciones');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 70) return '#10b981';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  const getOpportunityClass = (level) => {
    if (level === 'Alta') return 'opportunity-alta';
    if (level === 'Media') return 'opportunity-media';
    return 'opportunity-baja';
  };

  const getRecommendationType = (text) => {
    if (text.includes('RECOMENDADA')) return 'success';
    if (text.includes('EVALUAR') || text.includes('CONSIDERAR')) return 'warning';
    if (text.includes('RIESGO')) return 'danger';
    return 'info';
  };


  const handleDownloadPDF = async () => {
    if (!recommendations || !selectedZone) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/scoring/recommendations/${selectedZone}/pdf`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (!response.ok) throw new Error('Error al descargar');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `guia_accion_${recommendations.zone_name?.toLowerCase().replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError('Error al descargar el PDF');
    }
  };


  return (
    <div className="recommendations-page">
      {/* Hero Section */}
      <section className="recommendations-hero">
        <div className="hero-content">
          <div>
            <span className="hero-badge">Market Analytics</span>
            <h1 className="hero-title">Recomendaciones</h1>
            <p className="hero-subtitle">
              Análisis detallado y recomendaciones estratégicas por zona. Utilizamos modelos predictivos para identificar áreas de alto potencial basándonos en métricas de densidad y educación.
            </p>
          </div>
          <div className="hero-selector">
            <label className="selector-label">Selecciona una zona</label>
            <div className="selector-wrapper">
              <select
                value={selectedZone}
                onChange={(e) => setSelectedZone(e.target.value)}
                className="zone-select"
              >
                <option value="">Selecciona una zona...</option>
                {zones.map(zone => (
                  <option key={zone.zone_code} value={zone.zone_code}>
                    {zone.zone_name} (Score: {zone.score?.toFixed(1)})
                  </option>
                ))}
              </select>
              <span className="material-symbols-outlined select-icon">expand_more</span>
            </div>
            <button
              className="btn-get-recommendations"
              onClick={handleGetRecommendations}
              disabled={!selectedZone || loading}
            >
              {loading ? 'Analizando...' : 'Obtener Recomendaciones'}
            </button>
          </div>
        </div>
      </section>

      {error && (
        <div className="error-message">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}

      {recommendations && (
        <>
          {/* Score Card */}
          <section className="score-card">
            <div className="score-card-bg"></div>
            <div className="score-card-content">
              <div className="score-card-left">
                <h2 className="score-zone-name">{recommendations.zone_name}</h2>
                <div className="score-level">
                  <span className="level-badge">Nivel de Potencial</span>
                  <span className={`level-value ${getOpportunityClass(recommendations.opportunity_level)}`}>
                    {recommendations.opportunity_level}
                  </span>
                </div>
              </div>
              <div className="score-card-right">
                <div className="score-number-section">
                  <p className="score-label">Puntuación General</p>
                  <div className="score-number">
                    <span className="score-value" style={{ color: getScoreColor(recommendations.score_real) }}>
                      {recommendations.score_real?.toFixed(1)}
                    </span>
                    <span className="score-max">/100</span>
                  </div>
                </div>
                <div className="score-circle">
                  <div className="circle-progress" style={{
                    background: `conic-gradient(${getScoreColor(recommendations.score_real)} ${recommendations.score_real}%, #e2e8f0 ${recommendations.score_real}%)`
                  }}>
                    <div className="circle-inner">
                      <span className="material-symbols-outlined">trending_up</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Alert / Recommendation */}
          <section className={`alert-section alert-${getRecommendationType(recommendations.recommendation)}`}>
            <div className="alert-icon">
              <span className="material-symbols-outlined">assignment</span>
            </div>
            <div className="alert-content">
              <h4 className="alert-title">
                {recommendations.recommendation.split(':')[0]}
              </h4>
              <p className="alert-text">
                {recommendations.recommendation.split(':')[1]?.trim() || recommendations.recommendation}
              </p>
            </div>
          </section>

          {/* Bento Grid */}
          <section className="bento-grid">
            {/* Fortalezas */}
            <div className="bento-card strengths-card">
              <div className="bento-header">
                <div className="bento-title">
                  <div className="bento-icon strengths-icon">
                    <span className="material-symbols-outlined">thumb_up</span>
                  </div>
                  <h3>Fortalezas</h3>
                </div>
                <span className="bento-badge strengths-badge">Impulsores</span>
              </div>
              <div className="bento-content">
                {recommendations.strengths?.length > 0 ? (
                  recommendations.strengths.map((s, i) => (
                    <div key={i} className="bento-item">
                      <div className="bento-item-header">
                        <span className="bento-item-title">
                          {s.replace(/[🏘️💰🎓📊]/g, '').replace(/[+-]\d+\.?\d*\s*puntos/g, '').trim()}
                        </span>
                        <span className="bento-item-value">
                          {s.match(/[+-]\d+\.?\d*/)?.[0] || ''}
                        </span>
                      </div>
                      <div className="bento-progress">
                        <div className="bento-progress-fill" style={{
                          width: `${Math.min(100, (parseFloat(s.match(/[+-]?\d+\.?\d*/)?.[0]) || 0) * 2)}%`
                        }}></div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="bento-empty">
                    <span className="material-symbols-outlined">verified</span>
                    <p>Sin fortalezas destacables</p>
                  </div>
                )}
              </div>
            </div>

            {/* Debilidades */}
            <div className="bento-card weaknesses-card">
              <div className="bento-header">
                <div className="bento-title">
                  <div className="bento-icon weaknesses-icon">
                    <span className="material-symbols-outlined">build</span>
                  </div>
                  <h3>Debilidades</h3>
                </div>
                <span className="bento-badge weaknesses-badge">En Observación</span>
              </div>
              <div className="bento-content">
                {recommendations.weaknesses?.length > 0 && !recommendations.weaknesses[0].includes('Sin debilidades') ? (
                  recommendations.weaknesses.map((w, i) => (
                    <div key={i} className="bento-item">
                      <div className="bento-item-header">
                        <span className="bento-item-title">
                          {w.replace(/[🏘️💰🎓🏪]/g, '').replace(/[+-]\d+\.?\d*\s*puntos/g, '').trim()}
                        </span>
                        <span className="bento-item-value negative">
                          {w.match(/[+-]\d+\.?\d*/)?.[0] || ''}
                        </span>
                      </div>
                      <div className="bento-progress">
                        <div className="bento-progress-fill weaknesses-fill" style={{
                          width: `${Math.min(100, Math.abs(parseFloat(w.match(/[+-]?\d+\.?\d*/)?.[0]) || 0) * 2)}%`
                        }}></div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="bento-empty">
                    <span className="material-symbols-outlined">verified</span>
                    <p>Sin debilidades significativas detectadas</p>
                  </div>
                )}
              </div>
            </div>

            {/* Oportunidades */}
            <div className="bento-card opportunities-card">
              <div className="bento-header">
                <div className="bento-title">
                  <div className="bento-icon opportunities-icon">
                    <span className="material-symbols-outlined">rocket_launch</span>
                  </div>
                  <h3>Oportunidades</h3>
                </div>
                <span className="bento-badge opportunities-badge">Escalabilidad</span>
              </div>
              <div className="bento-content">
                {recommendations.opportunities?.length > 0 ? (
                  recommendations.opportunities.map((o, i) => (
                    <div key={i} className="bento-opportunity-item">
                      <div className="opportunity-line"></div>
                      <p className="opportunity-text">
                        {o.replace(/[🚀📈🌟🔮]/g, '').trim()}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="bento-empty">
                    <span className="material-symbols-outlined">explore</span>
                    <p>Genera predicciones ML para descubrir oportunidades</p>
                  </div>
                )}
              </div>
            </div>

            {/* Riesgos */}
            <div className="bento-card risks-card">
              <div className="bento-header">
                <div className="bento-title">
                  <div className="bento-icon risks-icon">
                    <span className="material-symbols-outlined">warning</span>
                  </div>
                  <h3>Riesgos</h3>
                </div>
                <span className="bento-badge risks-badge">Mitigación</span>
              </div>
              <div className="bento-content">
                {recommendations.risks?.length > 0 && !recommendations.risks[0].includes('No se detectaron') ? (
                  recommendations.risks.map((r, i) => (
                    <div key={i} className="bento-opportunity-item risk-item">
                      <div className="opportunity-line risk-line"></div>
                      <p className="opportunity-text">
                        {r.replace(/[⚠️📉]/g, '').trim()}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="bento-empty">
                    <span className="material-symbols-outlined">shield_lock</span>
                    <p>No se detectaron riesgos significativos</p>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Context Section */}
          <section className="context-section">
            <div className="context-card">
              <div className="context-card-bg"></div>
              <div className="context-card-content">
                <h3>Contexto de Mercado</h3>
                <p>
                  La zona de {recommendations.zone_name} mantiene una estabilidad competitiva frente al promedio regional.
                  El análisis de variables socioeconómicas permite identificar patrones de inversión estratégica.
                </p>
                <div className="context-stats">
                  <div className="context-stat">
                    <span className="context-stat-label">Score Real</span>
                    <span className="context-stat-value">{recommendations.score_real?.toFixed(1)}</span>
                  </div>
                  <div className="context-stat">
                    <span className="context-stat-label">Predicción ML</span>
                    <span className="context-stat-value">
                      {recommendations.prediction_ml?.toFixed(1) || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div className="action-card">
              <span className="material-symbols-outlined action-icon">auto_graph</span>
              <h4>Acción Sugerida</h4>
              <p>
                Mantener posición actual y diversificar inversiones basándose en el análisis de fortalezas y oportunidades detectadas.
              </p>
              <button className="btn-action" onClick={handleDownloadPDF}>
                Descargar Guía de Acción
              </button>
            </div>
          </section>
        </>
      )}

      {!recommendations && !loading && (
        <section className="empty-recommendations">
          <span className="material-symbols-outlined">lightbulb</span>
          <h3>Selecciona una zona para obtener recomendaciones</h3>
          <p>Elige una zona del selector y haz clic en "Obtener Recomendaciones"</p>
        </section>
      )}
    </div>
  );
};

export default RecommendationsPanel;