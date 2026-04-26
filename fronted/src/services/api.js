const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
  },

  // ========== INDICADORES ==========
  async getIndicators(zoneCode = null) {
    const token = localStorage.getItem('token');
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    let url = `${API_URL}/api/indicators/`;
    if (zoneCode) {
      url += `?zone_code=${zoneCode}`;
    }
    const response = await fetch(url, { headers });
    return handleResponse(response);
  },

  async calculateIndicators() {
    const token = localStorage.getItem('token');
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
    const response = await fetch(`${API_URL}/api/indicators/calculate`, {
      method: 'POST',
      headers,
    });
    return handleResponse(response);
  },

  // ========== CONFIGURACIÓN ==========
  async getProfiles() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/configuration/profiles`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  async getActiveProfile() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/configuration/profiles/active`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  async createProfile(profileData) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/configuration/profiles`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(profileData)
    });
    return handleResponse(response);
  },

  async updateProfile(profileId, profileData) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/configuration/profiles/${profileId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(profileData)
    });
    return handleResponse(response);
  },

  async activateProfile(profileId) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/configuration/profiles/${profileId}/activate`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  async getActiveWeights() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/configuration/weights/active`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  async deleteProfile(profileId) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/configuration/profiles/${profileId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  // ========== SCORING ==========
  async calculateScoring() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/scoring/calculate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return handleResponse(response);
  },

  async getScores(zoneCode = null) {
    const token = localStorage.getItem('token');
    let url = `${API_URL}/api/scoring/scores`;
    if (zoneCode) {
      url += `/${zoneCode}`;
    }
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  // ========== RANKING ==========
  async getRanking(limit = null, opportunityLevel = null) {
    const token = localStorage.getItem('token');
    let url = `${API_URL}/api/scoring/ranking`;
    const params = [];
    if (limit) params.push(`limit=${limit}`);
    if (opportunityLevel) params.push(`opportunity_level=${opportunityLevel}`);
    if (params.length) url += `?${params.join('&')}`;

    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  // ========== AUDITORÍA ==========
  async getAuditEvents(serviceName = null, eventType = null, limit = 100, offset = 0) {
    const token = localStorage.getItem('token');
    let url = `${API_URL}/api/audit/events?limit=${limit}&offset=${offset}`;
    if (serviceName) url += `&service_name=${serviceName}`;
    if (eventType) url += `&event_type=${eventType}`;

    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  async getAuditTrace(traceId) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/audit/events/trace/${traceId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  async getAuditStats() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/audit/stats`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  // ========== COMPARACIÓN ==========
  async compareZones(zoneCodes) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/scoring/compare`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ zone_codes: zoneCodes })
    });
    return handleResponse(response);
  }

};