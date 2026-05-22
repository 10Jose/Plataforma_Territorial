import React, { useState, useRef, useEffect } from 'react';
import '../styles/FileUploadModern.css';
import ZonesList from './ZonesList';
import IndicatorsTable from './IndicatorsTable';
import ConfigurationPanel from './ConfigurationPanel';
import { api } from '../services/api';
import ScoringTable from './ScoringTable';
import RankingTable from './RankingTable';
import AuditPanel from './AuditPanel';
import ZoneComparison from './ZoneComparison';
import DashboardHome from './DashboardHome';
import Sidebar from './Sidebar';
import RecommendationsPanel from './RecommendationsPanel';
import MLPanel from './MLPanel';

const FileUploadModern = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [refreshZones, setRefreshZones] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const fileInputRef = useRef(null);

  // Listener para cambio de pestaña desde el Dashboard
  useEffect(() => {
    const handleChangeTab = (event) => {
      setActiveTab(event.detail);
    };
    window.addEventListener('changeTab', handleChangeTab);
    return () => window.removeEventListener('changeTab', handleChangeTab);
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      setError('Solo se permiten archivos CSV.');
      setFile(null);
      return;
    }
    if (selectedFile.size === 0) {
      setError('El archivo está vacío (0 bytes). Por favor selecciona un archivo con datos.');
      setFile(null);
      return;
    }
    if (selectedFile.size > 25 * 1024 * 1024) {
      setError('El archivo excede el tamaño máximo permitido de 25MB.');
      setFile(null);
      return;
    }
    setError(null);
    setFile(selectedFile);
    setResult(null);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Por favor selecciona un archivo.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.loadFile(file);
      setResult(data);
      setRefreshZones(prev => !prev);
      setSyncing(true);
      setTimeout(() => setSyncing(false), 3000);
    } catch (err) {
      setError(err.detail || err.message || 'Error al cargar el archivo');
    } finally {
      setLoading(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen flex">
      {/* Sidebar - Barra lateral */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onLogout={handleLogout}
      />

      {/*  margen para la sidebar */}
      <div className="flex-1 ml-[260px]">
        {/* Header simplificado */}


        {/* Main Content */}
        <main className="main-content">
          <div className="container">
            {/* ========== DASHBOARD TAB ========== */}
            {activeTab === 'dashboard' && (
              <>
                <DashboardHome />

                <div className="hero" style={{ marginTop: '2rem' }}>
                  <h1>Analítica Territorial</h1>
                  <p>Carga tu archivo CSV con datos territoriales y obtén análisis inteligentes para tu negocio.</p>
                </div>

                <form onSubmit={handleSubmit}>
                  <div
                    className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                  >
                    <div className="upload-content">
                      <div className="icon-circle">
                        <span className="material-symbols-outlined upload-icon">cloud_upload</span>
                      </div>
                      <div>
                        <div className="upload-text">
                          {file ? file.name : 'Arrastra y suelta tu archivo .csv aquí'}
                        </div>
                        <div className="upload-subtext">
                          {file ? `${(file.size / 1024).toFixed(2)} KB` : 'o haz clic en el botón para buscar'}
                        </div>
                      </div>
                      <button type="button" className="primary-button" onClick={triggerFileInput} disabled={loading}>
                        <span className="material-symbols-outlined">upload_file</span>
                        {loading ? 'Subiendo...' : 'Seleccionar archivo'}
                      </button>
                    </div>
                    <input ref={fileInputRef} type="file" accept=".csv" onChange={handleFileChange} className="hidden-input" disabled={loading} />
                  </div>
                  {file && (
                    <div className="flex-center mt-6">
                      <button type="submit" disabled={loading} className="submit-button">
                        {loading ? 'Procesando...' : 'Subir archivo'}
                      </button>
                    </div>
                  )}
                </form>

                <div className="meta-info">
                  <span className="badge">Formatos soportados: .csv</span>
                  <span className="separator">•</span>
                  <span className="size-info">Tamaño máximo: 25MB</span>
                </div>

                {syncing && (
                  <div className="syncing-message">
                    <span className="material-symbols-outlined">sync</span>
                    Sincronizando zonas con el servidor...
                  </div>
                )}

                {error && (
                  <div className="error-message">
                    <strong>Error:</strong> {error}
                  </div>
                )}

                {result && (
                  <div className="success-message">
                    <h3>{result.status === 'already_loaded' ? '⚠️ Archivo ya cargado' : '✅ Carga exitosa:'}</h3>
                    <p><strong>Archivo:</strong> {result.filename}</p>
                    <p><strong>ID:</strong> {result.id}</p>
                    <p><strong>Total filas:</strong> {result.rows}</p>
                    <p><strong>Filas válidas:</strong> {result.valid_rows}</p>
                    <p><strong>Filas inválidas:</strong> {result.invalid_rows}</p>
                    {result.message && <p><strong>Mensaje:</strong> {result.message}</p>}
                    {result.errors && result.errors.length > 0 && (
                      <div className="error-summary">
                        <details>
                          <summary>⚠️ Ver errores detallados ({result.errors.length} fila(s) con problemas)</summary>
                          <div className="error-container">
                            {result.errors.map((err, idx) => (
                              <div key={idx} className="error-item">
                                <div className="error-title">🔴 Fila {err.row + 1}</div>
                                <ul className="error-list">{err.errors.map((error, i) => <li key={i}>{error}</li>)}</ul>
                                <details>
                                  <summary className="error-data-summary">📄 Mostrar datos originales</summary>
                                  <pre className="error-data-pre">{JSON.stringify(err.row_data, null, 2)}</pre>
                                </details>
                              </div>
                            ))}
                          </div>
                        </details>
                      </div>
                    )}
                    <details style={{ marginTop: '1rem' }}>
                      <summary className="json-summary">📦 Ver respuesta JSON completa</summary>
                      <pre className="json-pre">{JSON.stringify(result, null, 2)}</pre>
                    </details>
                  </div>
                )}

                <ZonesList refreshTrigger={refreshZones} />
              </>
            )}

            {activeTab === 'indicators' && <IndicatorsTable />}
            {activeTab === 'configuration' && <ConfigurationPanel />}
            {activeTab === 'scoring' && <ScoringTable />}
            {activeTab === 'ranking' && <RankingTable />}
            {activeTab === 'audit' && <AuditPanel />}
            {activeTab === 'comparison' && <ZoneComparison />}
            {activeTab === 'ml' && <MLPanel />}
            {activeTab === 'recommendations' && <RecommendationsPanel />}
          </div>
        </main>

        {/* Footer */}
        <footer className="footer">
          <div className="footer-content">
            <div className="copyright">© 2026 Todos los derechos reservados.</div>
            <div className="footer-links">
              <button onClick={() => alert('Política de Privacidad - Próximamente')} className="link-button">Política de Privacidad</button>
              <button onClick={() => alert('Términos de Servicio - Próximamente')} className="link-button">Términos de Servicio</button>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default FileUploadModern;