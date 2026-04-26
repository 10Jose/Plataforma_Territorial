import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import '../styles/AuditPanel.css';

const AuditPanel = () => {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({ serviceName: '', eventType: '' });
  const [selectedTrace, setSelectedTrace] = useState(null);
  const [traceEvents, setTraceEvents] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [eventsData, statsData] = await Promise.all([
        api.getAuditEvents(null, null, 100),
        api.getAuditStats()
      ]);
      setEvents(eventsData || []);
      setStats(statsData);
    } catch (err) {
      setError(err.message || 'Error al cargar datos de auditoría');
    } finally {
      setLoading(false);
    }
  };

  const handleFilter = async () => {
    setLoading(true);
    setError(null);
    try {
      const serviceName = filter.serviceName || null;
      const eventType = filter.eventType || null;
      const data = await api.getAuditEvents(serviceName, eventType, 100);
      setEvents(data || []);
      setCurrentPage(1);
    } catch (err) {
      setError(err.message || 'Error al filtrar eventos');
    } finally {
      setLoading(false);
    }
  };

  const handleViewTrace = async (traceId) => {
    try {
      const data = await api.getAuditTrace(traceId);
      console.log('Trace data:', data);
      setTraceEvents(data || []);
      setSelectedTrace(traceId);
    } catch (err) {
      setError(err.message || 'Error al cargar traza');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getStatusClass = (status) => {
    return status === 'success' ? 'status-success' : 'status-error';
  };

  const getEventTypeLabel = (eventType) => {
    const labels = {
      'scoring_calculate_started': 'Scoring Iniciado',
      'scoring_calculate_completed': 'Scoring Completado',
      'scoring_calculate_failed': 'Scoring Fallido',
      'indicators_calculate_started': 'Indicadores Iniciado',
      'indicators_calculate_completed': 'Indicadores Completado',
      'indicators_calculate_failed': 'Indicadores Fallido',
      'profile_create_started': 'Perfil Creado',
      'profile_create_completed': 'Perfil Creado',
      'profile_activate_started': 'Perfil Activado',
      'profile_activate_completed': 'Perfil Activado',
      'profile_delete_started': 'Perfil Eliminado',
      'profile_delete_completed': 'Perfil Eliminado',
      'profile_update_started': 'Perfil Actualizado',
      'profile_update_completed': 'Perfil Actualizado',
      'scaling_auto_triggered': 'Scaling Automático',
      'weights_loaded': 'Pesos Cargados',
    };
    return labels[eventType] || eventType;
  };

  const getServiceLabel = (serviceName) => {
    const labels = {
      'ms-analytics': 'Analytics',
      'ms-configuration': 'Configuración',
      'ms-ingestion': 'Ingesta',
      'ms-transformation': 'Transformación',
    };
    return labels[serviceName] || serviceName;
  };

  // Paginación
  const totalPages = Math.ceil(events.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedEvents = events.slice(startIndex, startIndex + itemsPerPage);

  // Opciones únicas para filtros
  const uniqueServices = [...new Set(events.map(e => e.service_name))];
  const uniqueEventTypes = [...new Set(events.map(e => e.event_type))];

  if (loading && events.length === 0) {
    return (
      <div className="audit-loading">
        <div className="spinner-large"></div>
        <p>Cargando auditoría...</p>
      </div>
    );
  }

  return (
    <div className="audit-container">
      {/* Header */}
      <div className="audit-header">
        <div>
          <h1 className="audit-title">Auditoría y Trazabilidad</h1>
          <p className="audit-subtitle">
            Registro de todas las operaciones del sistema
          </p>
        </div>
        <button className="btn-refresh" onClick={loadData}>
          <span className="material-symbols-outlined">refresh</span>
          Actualizar
        </button>
      </div>

      {/* Stats Summary */}
      {stats && (
        <div className="audit-stats">
          <div className="stat-card">
            <span className="stat-label">Total Eventos</span>
            <span className="stat-value">{stats.total_events}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Servicios Activos</span>
            <span className="stat-value">
              {stats.by_service ? Object.keys(stats.by_service).length : 0}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Tipos de Evento</span>
            <span className="stat-value">
              {stats.by_type ? Object.keys(stats.by_type).length : 0}
            </span>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="error-message">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}

      {/* Filtros */}
      <div className="audit-filters">
        <select
          className="filter-select"
          value={filter.serviceName}
          onChange={(e) => setFilter({ ...filter, serviceName: e.target.value })}
        >
          <option value="">Todos los servicios</option>
          {[...new Set(events.map(e => e.service_name).filter(Boolean))].map(service => (
                <option key={service} value={service}>{getServiceLabel(service)}</option>
              ))}
        </select>
        <select
          className="filter-select"
          value={filter.eventType}
          onChange={(e) => setFilter({ ...filter, eventType: e.target.value })}
        >
          <option value="">Todos los eventos</option>
          {[...new Set(events.map(e => e.event_type).filter(Boolean))].map(type => (
                <option key={type} value={type}>{getEventTypeLabel(type)}</option>
              ))}
        </select>
        <button className="btn-filter" onClick={handleFilter}>
          <span className="material-symbols-outlined">filter_alt</span>
          Filtrar
        </button>
        {(filter.serviceName || filter.eventType) && (
          <button
            className="btn-clear"
            onClick={() => { setFilter({ serviceName: '', eventType: '' }); loadData(); }}
          >
            Limpiar
          </button>
        )}
      </div>

      {/* Tabla de Eventos */}
      {events.length === 0 ? (
        <div className="empty-state">
          <span className="material-symbols-outlined">history</span>
          <h3>No hay eventos registrados</h3>
          <p>Los eventos aparecerán cuando se ejecuten operaciones en el sistema</p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Servicio</th>
                  <th>Evento</th>
                  <th>Usuario</th>
                  <th>Estado</th>
                  <th>Traza</th>
                </tr>
              </thead>
              <tbody>
                {paginatedEvents.map((event) => (
                  <tr key={event.id}>
                    <td className="date-cell">{formatDate(event.created_at)}</td>
                    <td>
                      <span className={`service-badge service-${event.service_name?.replace('ms-', '')}`}>
                        {getServiceLabel(event.service_name)}
                      </span>
                    </td>
                    <td>{getEventTypeLabel(event.event_type)}</td>
                    <td>{event.username || '-'}</td>
                    <td>
                      <span className={`status-badge ${getStatusClass(event.status)}`}>
                        {event.status === 'success' ? 'Éxito' : 'Error'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-trace"
                        onClick={() => handleViewTrace(event.trace_id)}
                        title="Ver traza completa"
                      >
                        <span className="material-symbols-outlined">link</span>
                        {event.trace_id?.substring(0, 8)}...
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

      {/* Modal de Traza */}
      {selectedTrace && (
        <div className="modal-overlay" onClick={() => { setSelectedTrace(null); setTraceEvents([]); }}>
          <div className="modal-content trace-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Traza: {selectedTrace}</h2>
              <button className="modal-close" onClick={() => { setSelectedTrace(null); setTraceEvents([]); }}>
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <div className="modal-body">
              {traceEvents.length === 0 ? (
                <p className="loading-trace">Cargando traza...</p>
              ) : (
                <div className="trace-timeline">
                  {traceEvents.map((event, index) => (
                    <div key={event.id} className="trace-event">
                      <div className="trace-time">
                        <span className="time-icon">{index + 1}</span>
                        <span className="time-text">{formatDate(event.created_at)}</span>
                      </div>
                      <div className="trace-details">
                        <span className={`trace-status ${getStatusClass(event.status)}`}></span>
                        <div>
                          <strong>{getServiceLabel(event.service_name)}</strong> - {getEventTypeLabel(event.event_type)}
                          {event.details_json && (
                            <pre className="trace-json">
                              {JSON.stringify(event.details_json, null, 2)}
                            </pre>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditPanel;