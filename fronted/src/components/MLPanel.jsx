import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import '../styles/MLPanel.css';

const MLPanel = () => {
  const [predictions, setPredictions] = useState([]);
  const [zones, setZones] = useState([]);
  const [selectedZone, setSelectedZone] = useState('');
  const [predictionResult, setPredictionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [predData, scoresData, expData] = await Promise.all([
        api.getMLPredictions(),
        api.getScores(),
        api.getMLExperiments()
      ]);
      setPredictions(predData || []);
      setZones(scoresData || []);
      setModelStatus(expData && expData.length > 0 ? expData[0] : null);
    } catch (err) {
      // Silencioso - puede no haber modelo entrenado aún
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async () => {
    if (!selectedZone) {
      setError('Selecciona una zona primero');
      return;
    }
    setLoading(true);
    setError(null);
    setPredictionResult(null);
    try {
      const result = await api.predictZone(selectedZone);
      setPredictionResult(result);
      await loadData();
    } catch (err) {
      if (err.message.includes('404') || err.message.includes('No hay')) {
        setError('No hay un modelo entrenado. Contacta al administrador.');
      } else {
        setError('Error al predecir: ' + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const getOpportunityClass = (label) => {
    if (label === 'Alta') return 'opportunity-high';
    if (label === 'Media') return 'opportunity-medium';
    return 'opportunity-low';
  };

  const handleRefresh = () => {
    loadData();
  };

  if (loading && predictions.length === 0) {
    return (
      <div className="ml-loading">
        <div className="spinner-large"></div>
        <p>Cargando predicciones...</p>
      </div>
    );
  }

  return (
    <div className="ml-container">
      {/* Header */}
      <div className="ml-header">
        <div>
          <h1 className="ml-title">Predicción de Potencial</h1>
          <p className="ml-subtitle">
            Estima el potencial territorial usando inteligencia artificial
          </p>
        </div>
        <button className="btn-refresh" onClick={handleRefresh}>
          <span className="material-symbols-outlined">refresh</span>
          Actualizar
        </button>
      </div>

      {/* Estado del modelo */}
      {modelStatus && (
        <div className="model-status-bar">
          <span className="material-symbols-outlined">check_circle</span>
          <span>Modelo predictivo activo | Precisión R²: {modelStatus.metric_value?.toFixed(2) || 'N/A'}</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="error-message">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}

      <div className="ml-grid">
        {/* Left Column - Predecir */}
        <div className="ml-left">
          <div className="ml-card">
            <h2>Estimar Potencial de una Zona</h2>
            <p className="card-desc">
              Selecciona una zona para obtener una predicción de su potencial basada en datos históricos
            </p>

            <div className="form-group">
              <label>Zona a analizar</label>
              <select
                value={selectedZone}
                onChange={(e) => setSelectedZone(e.target.value)}
                className="form-select"
              >
                <option value="">Selecciona una zona...</option>
                {zones.map(zone => (
                  <option key={zone.zone_code} value={zone.zone_code}>
                    {zone.zone_name}
                  </option>
                ))}
              </select>
            </div>

            <button
              className="btn-predict"
              onClick={handlePredict}
              disabled={!selectedZone || loading}
            >
              <span className="material-symbols-outlined">query_stats</span>
              {loading ? 'Analizando...' : 'Estimar Potencial'}
            </button>

            {predictionResult && (
              <div className="prediction-result-card">
                <h3>{predictionResult.zone_name}</h3>
                <div className="prediction-main">
                  <div className="prediction-score">
                    <span className="pred-label">Potencial Estimado</span>
                    <span className={`pred-value-large ${getOpportunityClass(predictionResult.prediction_label)}`}>
                      {predictionResult.predicted_value?.toFixed(1)}
                    </span>
                  </div>
                  <div className="prediction-level">
                    <span className="pred-label">Clasificación</span>
                    <span className={`opportunity-badge-large ${getOpportunityClass(predictionResult.prediction_label)}`}>
                      {predictionResult.prediction_label}
                    </span>
                  </div>
                </div>
                <p className="prediction-note">
                  * Esta predicción se basa en el modelo entrenado con datos históricos de todas las zonas.
                </p>
              </div>
            )}
          </div>

          {/* Info card */}
          <div className="ml-card info-card">
            <span className="material-symbols-outlined info-icon">lightbulb</span>
            <div>
              <h3>¿Cómo funciona?</h3>
              <p>
                El sistema analiza patrones en los datos históricos (población, ingreso, educación, competencia)
                para estimar el potencial de nuevas zonas. Cuantos más datos se carguen, más precisas serán las predicciones.
              </p>
            </div>
          </div>
        </div>

        {/* Right Column - Historial */}
        <div className="ml-right">
          <div className="ml-card">
            <h2>Predicciones Recientes</h2>
            {predictions.length === 0 ? (
              <div className="empty-section">
                <span className="material-symbols-outlined">query_stats</span>
                <p>No hay predicciones realizadas aún</p>
                <p className="empty-hint">Selecciona una zona y haz clic en "Estimar Potencial"</p>
              </div>
            ) : (
              <div className="predictions-list">
                {predictions.slice(0, 10).map(pred => {
                  const actualScore = zones.find(z => z.zone_code === pred.zone_code)?.score;
                  return (
                    <div key={pred.id} className="prediction-item">
                      <div className="pred-header">
                        <span className="pred-zone">{pred.zone_name}</span>
                        <span className={`pred-value ${getOpportunityClass(pred.prediction_label)}`}>
                          {pred.prediction_value?.toFixed(1)}
                        </span>
                      </div>
                      <div className="pred-footer">
                        <span className={`opportunity-badge ${getOpportunityClass(pred.prediction_label)}`}>
                          {pred.prediction_label}
                        </span>
                        {actualScore !== undefined && (
                          <span className="actual-score">
                            Score real: {actualScore.toFixed(1)}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MLPanel;