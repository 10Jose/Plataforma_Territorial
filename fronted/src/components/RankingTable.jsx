import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import '../styles/RankingTable.css';

const RankingTable = () => {
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [showTop10, setShowTop10] = useState(true);

  const loadRanking = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const limit = showTop10 ? 10 : null;
      const level = filter === 'all' ? null : filter;
      const data = await api.getRanking(limit, level);
      setRanking(data || []);
    } catch (err) {
      setError(err.message || 'Error al cargar ranking');
    } finally {
      setLoading(false);
    }
  }, [filter, showTop10]);

  useEffect(() => {
    loadRanking();
  }, [loadRanking]);

  const getOpportunityClass = (level) => {
    if (level === 'Alta') return 'opportunity-high';
    if (level === 'Media') return 'opportunity-medium';
    return 'opportunity-low';
  };

  const getRankClass = (position) => {
    if (position === 1) return 'rank-first';
    if (position === 2) return 'rank-second';
    if (position === 3) return 'rank-third';
    return '';
  };

  const getMedalIcon = (position) => {
    if (position === 1) return '🥇';
    if (position === 2) return '🥈';
    if (position === 3) return '🥉';
    return position;
  };

  // Datos para gráfico de barras
  const chartData = ranking.slice(0, 10);
  const maxScore = Math.max(...chartData.map(d => d.score), 1);

  if (loading) {
    return (
      <div className="ranking-loading">
        <div className="spinner-large"></div>
        <p>Cargando ranking...</p>
      </div>
    );
  }

  return (
    <div className="ranking-container">
      {/* Header */}
      <div className="ranking-header">
        <div>
          <h1 className="ranking-title">Ranking de Zonas</h1>
          <p className="ranking-subtitle">
            Zonas ordenadas por potencial de oportunidad
          </p>
        </div>
        <div className="ranking-controls">
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={showTop10}
              onChange={(e) => setShowTop10(e.target.checked)}
            />
            <span className="toggle-slider"></span>
            <span className="toggle-label">Top 10</span>
          </label>
          <select
            className="filter-select"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">Todas</option>
            <option value="Alta">Alta Oportunidad</option>
            <option value="Media">Media Oportunidad</option>
            <option value="Baja">Baja Oportunidad</option>
          </select>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="error-message">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}

      {ranking.length === 0 ? (
        <div className="empty-state">
          <span className="material-symbols-outlined">leaderboard</span>
          <h3>No hay ranking disponible</h3>
          <p>Calcula el scoring primero para ver el ranking</p>
        </div>
      ) : (
        <div className="ranking-content">
          {/* Gráfico de Barras */}
          <div className="chart-container">
            <h3 className="chart-title">Top 10 - Scores</h3>
            <div className="bar-chart">
              {chartData.map((item) => (
                <div key={item.zone_code} className="bar-item">
                  <div className="bar-label">
                    <span className={`rank-medal ${getRankClass(item.rank_position)}`}>
                      {getMedalIcon(item.rank_position)}
                    </span>
                    <span className="bar-zone">{item.zone_name}</span>
                  </div>
                  <div className="bar-wrapper">
                    <div
                      className={`bar-fill ${getOpportunityClass(item.opportunity_level)}`}
                      style={{ width: `${(item.score / maxScore) * 100}%` }}
                    >
                      <span className="bar-value">{item.score.toFixed(1)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Tabla de Ranking */}
          <div className="table-container">
            <table className="ranking-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Zona</th>
                  <th className="text-right">Score</th>
                  <th className="text-center">Oportunidad</th>
                  <th className="text-right">Población</th>
                  <th className="text-right">Ingreso</th>
                  <th className="text-right">Educación</th>
                </tr>
              </thead>
              <tbody>
                {ranking.map((item) => (
                  <tr key={item.zone_code} className={getRankClass(item.rank_position)}>
                    <td className="rank-cell">
                      <span className={`rank-badge ${getRankClass(item.rank_position)}`}>
                        {getMedalIcon(item.rank_position)}
                      </span>
                    </td>
                    <td className="zone-name">{item.zone_name}</td>
                    <td className="text-right score-value">{item.score.toFixed(1)}</td>
                    <td className="text-center">
                      <span className={`opportunity-badge ${getOpportunityClass(item.opportunity_level)}`}>
                        {item.opportunity_level}
                      </span>
                    </td>
                    <td className="text-right contribution-positive">
                      +{item.contributions?.population || 0}
                    </td>
                    <td className="text-right contribution-positive">
                      +{item.contributions?.income || 0}
                    </td>
                    <td className="text-right contribution-positive">
                      +{item.contributions?.education || 0}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default RankingTable;