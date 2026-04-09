import React, { useState, useRef } from 'react';
import './FileUploadModern.css';
import ZonesList from './ZonesList';
import { api } from '../services/api';

const FileUploadModern = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [refreshZones, setRefreshZones] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const fileInputRef = useRef(null);

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
      // Usar el interceptor api.loadFile
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

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="header">
        <nav className="nav">
          <div className="logo">Plataforma Territorial</div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Hero */}
          <div className="hero">
            <h1>Analítica Territorial</h1>
            <p>Carga tu archivo CSV con datos territoriales y obtén análisis inteligentes para tu negocio.</p>
          </div>

          {/* Upload Zone */}
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
                <button
                  type="button"
                  className="primary-button"
                  onClick={triggerFileInput}
                  disabled={loading}
                >
                  <span className="material-symbols-outlined">upload_file</span>
                  {loading ? 'Subiendo...' : 'Seleccionar archivo'}
                </button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden-input"
                disabled={loading}
              />
            </div>

            {/* Submit Button */}
            {file && (
              <div className="flex-center mt-6">
                <button
                  type="submit"
                  disabled={loading}
                  className="submit-button"
                >
                  {loading ? 'Procesando...' : 'Subir archivo'}
                </button>
              </div>
            )}
          </form>

          {/* Meta Info */}
          <div className="meta-info">
            <span className="badge">Formatos soportados: .csv</span>
            <span className="separator">•</span>
            <span className="size-info">Tamaño máximo: 25MB</span>
          </div>

          {/* Mensaje de sincronización */}
          {syncing && (
            <div className="syncing-message">
              <span className="material-symbols-outlined" style={{ fontSize: '1rem' }}>sync</span>
              Sincronizando zonas con el servidor...
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Result Display */}
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
                    <summary>
                      ⚠️ Ver errores detallados ({result.errors.length} fila(s) con problemas)
                    </summary>
                    <div className="error-container">
                      {result.errors.map((err, idx) => (
                        <div key={idx} className="error-item">
                          <div className="error-title">
                            🔴 Fila {err.row + 1}
                          </div>
                          <ul className="error-list">
                            {err.errors.map((error, i) => (
                              <li key={i}>{error}</li>
                            ))}
                          </ul>
                          <details>
                            <summary className="error-data-summary">
                              📄 Mostrar datos originales
                            </summary>
                            <pre className="error-data-pre">
                              {JSON.stringify(err.row_data, null, 2)}
                            </pre>
                          </details>
                        </div>
                      ))}
                    </div>
                  </details>
                </div>
              )}

              <details style={{ marginTop: '1rem' }}>
                <summary className="json-summary">
                  📦 Ver respuesta JSON completa
                </summary>
                <pre className="json-pre">{JSON.stringify(result, null, 2)}</pre>
              </details>
            </div>
          )}

          <ZonesList refreshTrigger={refreshZones} />
        </div>
      </main>

      {/* Background Decorations */}
      <div className="bg-decoration"></div>
      <div className="bg-decoration-left"></div>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="copyright">© 2026 Todos los derechos reservados.</div>
          <div className="footer-links">
            <button
              onClick={() => alert('Política de Privacidad - Próximamente')}
              className="link-button"
            >
              Política de Privacidad
            </button>
            <button
              onClick={() => alert('Términos de Servicio - Próximamente')}
              className="link-button"
            >
              Términos de Servicio
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default FileUploadModern;