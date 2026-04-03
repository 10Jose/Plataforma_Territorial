import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import '../styles/auth.css';

const Login = ({ onSwitchToRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login, error } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      // El backend espera username, pero usamos email como username por simplicidad
      await login(username, password);
      window.location.href = '/dashboard';
    } catch (err) {
      // Error ya manejado en AuthContext
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-[440px]">
      <header className="flex flex-col items-center mb-12">
        <div className="text-center">
          <h2 className="font-headline font-bold text-3xl text-on-surface tracking-tight mb-2">
            Bienvenido
          </h2>
          <p className="text-on-surface-variant font-medium">
            Accede y explora la mejor opción para tu negocio
          </p>
        </div>
      </header>

      <div className="card">
        <form onSubmit={handleSubmit}>
          {/* Email / Username Field */}
          <div className="form-group">
            <label className="form-label">Username</label>
            <div className="input-wrapper">
              <span className="material-symbols-outlined input-icon">person</span>
              <input
                type="text"
                className="input-field"
                placeholder="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Password Field */}
          <div className="form-group">
            <div className="flex justify-between items-center">
              <label className="form-label">Password</label>
            </div>
            <div className="input-wrapper">
              <span className="material-symbols-outlined input-icon">lock</span>
              <input
                type={showPassword ? 'text' : 'password'}
                className="input-field"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                <span className="material-symbols-outlined">
                  {showPassword ? 'visibility_off' : 'visibility'}
                </span>
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <div className="pt-2">
            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading ? <div className="spinner"></div> : null}
              Login
              <span className="material-symbols-outlined text-lg">arrow_forward</span>
            </button>
          </div>
        </form>

        <div className="divider">
          <p className="text-sm text-on-surface-variant font-medium">
            Don't have an account yet?
          </p>
          <button onClick={onSwitchToRegister} className="btn-outline">
            Create an Account
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;