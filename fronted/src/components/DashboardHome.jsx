import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import '../styles/DashboardHome.css';

const DashboardHome = () => {
  const [stats, setStats] = useState({
    totalZones: 0,
    scoredZones: 0,
    predictedZones: 0,
    activeProfile: null,
    lastScoring: null,
    highOpportunity: 0,
    avgScore: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [scores, profiles, predictions] = await Promise.all([
        api.getScores().catch(() => []),
        api.getActiveProfile().catch(() => null),
        api.getMLPredictions().catch(() => [])
      ]);

      const activeProfile = profiles;
      const zonesCount = scores.length;
      const scoredCount = scores.filter(s => s.score > 0).length;
      const highOpp = scores.filter(s => s.opportunity_level === 'Alta').length;
      const avg = zonesCount > 0
        ? scores.reduce((sum, s) => sum + s.score, 0) / zonesCount
        : 0;

      setStats({
        totalZones: zonesCount,
        scoredZones: scoredCount,
        predictedZones: predictions.length,
        activeProfile: activeProfile,
        lastScoring: scores.length > 0 ? new Date().toLocaleDateString('es-ES') : null,
        highOpportunity: highOpp,
        avgScore: avg.toFixed(1)
      });
    } catch (err) {
      // Silencioso
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner-large"></div>
        <p>Cargando dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-home">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title" style={{
            fontSize: '2.75rem',
            fontWeight: 800,
            color: '#0f172a',
            letterSpacing: '-0.02em'
          }}>
            Panel de Control
          </h1>
          <p className="dashboard-subtitle">
            Visión general del sistema de analítica territorial
          </p>
        </div>
        <button className="btn-refresh" onClick={loadDashboardData}>
          <span className="material-symbols-outlined">refresh</span>
          Actualizar
        </button>
      </div>

      {/* KPIs Grid */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: '#dbeafe', color: '#2563eb' }}>
            <span className="material-symbols-outlined">map</span>
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Total Zonas</span>
            <span className="kpi-value">{stats.totalZones}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: '#d1fae5', color: '#059669' }}>
            <span className="material-symbols-outlined">trending_up</span>
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Alta Oportunidad</span>
            <span className="kpi-value">{stats.highOpportunity}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: '#fef3c7', color: '#d97706' }}>
            <span className="material-symbols-outlined">analytics</span>
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Score Promedio</span>
            <span className="kpi-value">{stats.avgScore}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: '#ede9fe', color: '#7c3aed' }}>
            <span className="material-symbols-outlined">psychology</span>
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Predicciones ML</span>
            <span className="kpi-value">{stats.predictedZones}</span>
          </div>
        </div>
      </div>

      {/* Quick Actions Grid */}
      <div className="actions-grid">
        <h2>Accesos Rápidos</h2>
        <div className="action-cards">
          <div className="action-card" onClick={() => window.dispatchEvent(new CustomEvent('changeTab', { detail: 'scoring' }))}>
            <span className="material-symbols-outlined">calculate</span>
            <div>
              <h3>Calcular Scoring</h3>
              <p>Evalúa el potencial de las zonas</p>
            </div>
          </div>

          <div className="action-card" onClick={() => window.dispatchEvent(new CustomEvent('changeTab', { detail: 'indicators' }))}>
            <span className="material-symbols-outlined">table_chart</span>
            <div>
              <h3>Ver Indicadores</h3>
              <p>Consulta datos demográficos</p>
            </div>
          </div>

          <div className="action-card" onClick={() => window.dispatchEvent(new CustomEvent('changeTab', { detail: 'configuration' }))}>
            <span className="material-symbols-outlined">tune</span>
            <div>
              <h3>Configurar Pesos</h3>
              <p>Ajusta parámetros del modelo</p>
            </div>
          </div>

          <div className="action-card" onClick={() => window.dispatchEvent(new CustomEvent('changeTab', { detail: 'ranking' }))}>
            <span className="material-symbols-outlined">leaderboard</span>
            <div>
              <h3>Ver Ranking</h3>
              <p>Zonas ordenadas por potencial</p>
            </div>
          </div>

          <div className="action-card" onClick={() => window.dispatchEvent(new CustomEvent('changeTab', { detail: 'ml' }))}>
            <span className="material-symbols-outlined">query_stats</span>
            <div>
              <h3>Predicción ML</h3>
              <p>Estima potencial con IA</p>
            </div>
          </div>

          <div className="action-card" onClick={() => window.dispatchEvent(new CustomEvent('changeTab', { detail: 'recommendations' }))}>
            <span className="material-symbols-outlined">lightbulb</span>
            <div>
              <h3>Recomendaciones</h3>
              <p>Análisis y guías de acción</p>
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <div className="status-item">
          <span className="status-dot active"></span>
          <span>Perfil Activo: {stats.activeProfile?.name || 'No configurado'}</span>
        </div>
        <div className="status-item">
          <span className="status-dot"></span>
          <span>Último Scoring: {stats.lastScoring || 'No realizado'}</span>
        </div>
        <div className="status-item">
          <span className="status-dot"></span>
          <span>Zonas Evaluadas: {stats.scoredZones}/{stats.totalZones}</span>
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;