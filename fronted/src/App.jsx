import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './components/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedRoute from './components/ProtectedRoute';
import FileUploadModern from './components/FileUploadModern';
import './styles/auth.css';

// Componente que muestra Login/Registro
const AuthContainer = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="min-h-screen auth-bg">
      <header className="header">
        <div className="header-content">
          <div className="flex items-center gap-3">
            <div className="logo-icon">
              <span className="material-symbols-outlined">landscape</span>
            </div>
            <h1 className="logo-text">Analytical Sanctuary</h1>
          </div>
        </div>
      </header>

      <main className="flex-grow flex items-center justify-center p-6 md:p-10">
        {isLogin ? (
          <Login onSwitchToRegister={() => setIsLogin(false)} />
        ) : (
          <Register onSwitchToLogin={() => setIsLogin(true)} />
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <div className="copyright">© 2024 Territorial Analytics. All rights reserved.</div>
          <div className="footer-links">
            <a href="#" className="footer-link">Privacy Policy</a>
            <a href="#" className="footer-link">Terms of Service</a>
            <a href="#" className="footer-link">Help Center</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Dashboard protegido (solo después de login)
const Dashboard = () => {
  const { user, logout } = useAuth();

  return (
    <div>
      {/* Barra superior */}
      <div style={{
        backgroundColor: '#0d9488',
        color: 'white',
        padding: '1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h1>Analytical Sanctuary</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span>Welcome, {user?.full_name || user?.username}</span>
          <button
            onClick={logout}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'rgba(255,255,255,0.2)',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              color: 'white'
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Componente de carga de CSV */}
      <div style={{ padding: '1.5rem' }}>
        <FileUploadModern />
      </div>
    </div>
  );
};

// Componente principal
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<AuthContainer />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;