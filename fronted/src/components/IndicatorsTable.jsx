import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const IndicatorsTable = () => {
  const [indicators, setIndicators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [refreshing, setRefreshing] = useState(false);
  const itemsPerPage = 5;

  const [stats, setStats] = useState({
    totalPopulation: 0,
    avgIncome: 0,
    populationTrend: '+12%',
    incomeUnit: 'Anual'
  });

  const fetchIndicators = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getIndicators();
      setIndicators(data || []);

      const totalPop = (data || []).reduce((sum, item) => sum + (item.population || 0), 0);
      const avgInc = (data || []).reduce((sum, item) => sum + (item.income || 0), 0) / (data?.length || 1);

      setStats({
        totalPopulation: totalPop,
        avgIncome: Math.round(avgInc),
        populationTrend: '+12%',
        incomeUnit: 'Anual'
      });
    } catch (err) {
      setError(err.message || 'Error al cargar indicadores');
    } finally {
      setLoading(false);
    }
  };

  const refreshIndicators = async () => {
    setRefreshing(true);
    setError(null);
    try {
      await api.calculateIndicators();
      await new Promise(resolve => setTimeout(resolve, 300));
      await fetchIndicators();
    } catch (err) {
      // Si es "No hay datos", NO mostrar error, mostrar vista vacía
      if (err.message.includes('No hay datos') || err.message.includes('404')) {
        setIndicators([]);
        setStats({
          totalPopulation: 0,
          avgIncome: 0,
          populationTrend: '+12%',
          incomeUnit: 'Anual'
        });
        setError(null); // ← Esto evita que se muestre el mensaje de error
      } else {
        setError(err.message || 'Error al actualizar indicadores');
      }
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchIndicators();
  }, []);

  const totalPages = Math.ceil(indicators.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedIndicators = indicators.slice(startIndex, startIndex + itemsPerPage);

  const getCompetitionClass = (level) => {
    if (level === 'Alta') return 'high';
    if (level === 'Media') return 'medium';
    return 'low';
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(0) + 'k';
    return num.toLocaleString();
  };

  if (loading && !refreshing) {
    return (
      <div className="indicators-loading">
        <div className="spinner"></div>
        <p>Cargando indicadores...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="indicators-error">
        <p>Error: {error}</p>
        <button onClick={refreshIndicators} className="retry-button">Reintentar</button>
      </div>
    );
  }

  if (indicators.length === 0) {
    return (
      <div className="indicators-empty">
        <h3>📊 Indicadores territoriales</h3>
        <p>No hay indicadores disponibles. Carga un archivo CSV y presiona "Actualizar".</p>
        <button onClick={refreshIndicators} className="refresh-button" disabled={refreshing}>
          {refreshing ? 'Actualizando...' : 'Actualizar'}
        </button>
      </div>
    );
  }

  return (
    <div className="indicators-container">
      {/* Header Section */}
      <div className="indicators-header-wrapper">
        <div>
          <h1 className="indicators-title">Datos Procesados</h1>
          <p className="indicators-subtitle">Visualización detallada de la segmentación demográfica por región.</p>
        </div>
        <button onClick={refreshIndicators} className="refresh-data-button" disabled={refreshing}>
          <span className="material-symbols-outlined">refresh</span>
          {refreshing ? 'Actualizando...' : 'Actualizar'}
        </button>
      </div>

      {/* Stats Overview */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Total Población</span>
          <div className="stat-value">
            <span className="stat-number">{formatNumber(stats.totalPopulation)}</span>
            <span className="stat-trend">{stats.populationTrend}</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '65%' }}></div>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-label">Ingreso Promedio</span>
          <div className="stat-value">
            <span className="stat-number">${formatNumber(stats.avgIncome)}</span>
            <span className="stat-unit">{stats.incomeUnit}</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '42%' }}></div>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="data-table-container">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Zona</th>
                <th className="text-right">Población</th>
                <th className="text-right">Ingreso</th>
                <th className="text-center">Educación (años)</th>
                <th>Competencia</th>
                <th>Fecha cálculo</th>
              </tr>
            </thead>
            <tbody>
              {paginatedIndicators.map((item) => {
                const levelClass = getCompetitionClass(item.competition_level);
                return (
                  <tr key={item.id}>
                    <td>
                      <div className="zone-cell">
                        <div className={`zone-dot competition-${levelClass}`}></div>
                        <span className="zone-name">{item.zone_name}</span>
                      </div>
                    </td>
                    <td className="text-right">{formatNumber(item.population)}</td>
                    <td className="text-right">${formatNumber(item.income)}</td>
                    <td className="text-center">{item.education}</td>
                    <td>
                      <span className={`competition-badge competition-${levelClass}`}>
                        {item.competition_level || 'Baja'}
                      </span>
                    </td>
                    <td>{new Date(item.calculated_at).toLocaleDateString()}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="pagination">
            <span className="pagination-info">
              Mostrando {startIndex + 1} - {Math.min(startIndex + itemsPerPage, indicators.length)} de {indicators.length} entradas
            </span>
            <div className="pagination-buttons">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="pagination-btn"
              >
                <span className="material-symbols-outlined">chevron_left</span>
              </button>
              {[...Array(totalPages)].map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentPage(i + 1)}
                  className={`pagination-page ${currentPage === i + 1 ? 'active' : ''}`}
                >
                  {i + 1}
                </button>
              ))}
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="pagination-btn"
              >
                <span className="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IndicatorsTable;