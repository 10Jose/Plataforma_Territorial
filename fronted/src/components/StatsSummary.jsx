import React from 'react';
import '../styles/StatsSummary.css';

const StatsSummary = ({ scores }) => {
  const totalZones = scores.length;
  const highOpportunity = scores.filter(s => s.opportunity_level === 'Alta').length;
  const avgScore = totalZones > 0
    ? (scores.reduce((sum, s) => sum + s.score, 0) / totalZones).toFixed(1)
    : '0.0';
  const bestScore = totalZones > 0
    ? scores[0]?.score.toFixed(1)
    : '0.0';

  return (
    <div className="stats-grid">
      {/* Zonas Evaluadas */}
      <div className="stat-card stat-card-general">
        <div className="stat-decoration"></div>
        <div className="stat-header">
          <span className="material-symbols-outlined stat-icon">map</span>
          <span className="stat-badge">General</span>
        </div>
        <div className="stat-content">
          <h4 className="stat-label">Zonas Evaluadas</h4>
          <p className="stat-value">{totalZones}</p>
        </div>
      </div>

      {/* Alta Oportunidad */}
      <div className="stat-card stat-card-opportunity">
        <div className="stat-decoration"></div>
        <div className="stat-header">
          <span className="material-symbols-outlined stat-icon">trending_up</span>
          <span className="stat-badge">Oportunidad</span>
        </div>
        <div className="stat-content">
          <h4 className="stat-label">Alta Oportunidad</h4>
          <p className="stat-value">{highOpportunity}</p>
        </div>
      </div>

      {/* Score Promedio */}
      <div className="stat-card stat-card-performance">
        <div className="stat-decoration"></div>
        <div className="stat-header">
          <span className="material-symbols-outlined stat-icon">analytics</span>
          <span className="stat-badge">Rendimiento</span>
        </div>
        <div className="stat-content">
          <h4 className="stat-label">Score Promedio</h4>
          <p className="stat-value">{avgScore}</p>
        </div>
      </div>

      {/* Mejor Zona */}
      <div className="stat-card stat-card-best">
        <div className="stat-decoration"></div>
        <div className="stat-header">
          <span className="material-symbols-outlined stat-icon filled">stars</span>
          <span className="stat-badge">Máximo</span>
        </div>
        <div className="stat-content">
          <h4 className="stat-label">Mejor Zona</h4>
          <p className="stat-value">{bestScore}</p>
        </div>
      </div>
    </div>
  );
};

export default StatsSummary;