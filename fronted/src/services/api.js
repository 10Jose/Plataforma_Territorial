const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Función para formatear errores como string
const formatError = (data, response) => {
  if (data.detail && Array.isArray(data.detail)) {
    return data.detail.map(err => err.msg).join(', ');
  }
  if (data.detail && typeof data.detail === 'string') {
    return data.detail;
  }
  if (data.message) {
    return data.message;
  }
  return `Error ${response.status}: ${response.statusText}`;
};

const handleResponse = async (response) => {
  if (!response.ok) {
    let errorMessage = `Error ${response.status}: ${response.statusText}`;
    try {
      const data = await response.json();
      errorMessage = formatError(data, response);
    } catch {
      // Si no se puede parsear JSON, usar mensaje por defecto
    }
    throw new Error(errorMessage);
  }
  return response.json();
};

export const api = {
  async loadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('token');
    const headers = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // ✅ Usar URL con barra al final para evitar redirección 307
    const response = await fetch(`${API_URL}/api/load/`, {
      method: 'POST',
      headers,
      body: formData,
    });

    return handleResponse(response);
  },

  async getZones(skip = 0, limit = 100) {
    const token = localStorage.getItem('token');
    const headers = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}/api/zones/?skip=${skip}&limit=${limit}`, {
      headers,
    });
    return handleResponse(response);
  },

  async getDatasets(skip = 0, limit = 100, validationStatus = null) {
    let url = `${API_URL}/api/datasets?skip=${skip}&limit=${limit}`;
    if (validationStatus) {
      url += `&validation_status=${validationStatus}`;
    }

    const token = localStorage.getItem('token');
    const headers = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, { headers });
    return handleResponse(response);
  }
};