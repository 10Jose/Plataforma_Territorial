const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const handleError = async (response) => {
  try {
    const data = await response.json();
    if (data.detail && Array.isArray(data.detail)) {
      const messages = data.detail.map(err => err.msg).join(', ');
      throw new Error(messages);
    }
    if (typeof data.detail === 'string') {
      throw new Error(data.detail);
    }
    if (data.message) {
      throw new Error(data.message);
    }
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  } catch (e) {
    if (e.message) throw e;
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
};

export const authService = {
  async register(userData) {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    if (!response.ok) {
      await handleError(response);
    }
    return response.json();
  },

  async login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await fetch(`${API_URL}/api/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    if (!response.ok) {
      await handleError(response);
    }
    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    return data;
  },

  async getMe() {
    const token = localStorage.getItem('token');
    if (!token) return null;
    const response = await fetch(`${API_URL}/api/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!response.ok) {
      localStorage.removeItem('token');
      return null;
    }
    return response.json();
  },

  logout() {
    localStorage.removeItem('token');
  },

  getToken() {
    return localStorage.getItem('token');
  },
};