import React, { useState } from 'react';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    // Validación de extensión en frontend
    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      setError('Solo se permiten archivos CSV.');
      setFile(null);
      return;
    }

    // Validación de archivo vacío (0 bytes)
    if (selectedFile.size === 0) {
      setError('El archivo está vacío (0 bytes).');
      setFile(null);
      return;
    }

    setError(null);
    setFile(selectedFile);
    setResult(null);
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

    const formData = new FormData();
    formData.append('file', file);

    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/load`, {
        method: 'POST',
        body: formData,
      });


      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        // Si no es JSON, usar texto plano
        const text = await response.text();
        data = { detail: text || `Error ${response.status}: ${response.statusText}` };
      }

      if (!response.ok) {
        throw new Error(data.detail || `Error ${response.status}: ${response.statusText}`);
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', padding: '2rem', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>Cargar Dataset CSV</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            disabled={loading}
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
        <button
          type="submit"
          disabled={loading || !file}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: '#61dafb',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {loading ? 'Subiendo...' : 'Subir'}
        </button>
      </form>

      {error && (
        <div style={{ marginTop: '1rem', padding: '10px', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '1rem', padding: '10px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '4px' }}>
          <h3>Resultado:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default FileUpload;