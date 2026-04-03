import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import '../styles/auth.css';

const Register = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const { register, error } = useAuth();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await register(formData);
      setSuccess(true);
      setTimeout(() => onSwitchToLogin(), 2000);
    } catch (err) {
      console.error('Registration failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="w-full max-w-[440px]">
        <div className="card text-center">
          <div style={{ width: '4rem', height: '4rem', backgroundColor: 'rgba(13,148,136,0.2)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
            <span className="material-symbols-outlined" style={{ color: 'var(--primary)', fontSize: '2rem' }}>check_circle</span>
          </div>
          <h3 className="font-headline font-bold text-xl mb-2">Account Created!</h3>
          <p className="text-on-surface-variant mb-4">
            Your account has been created successfully.
          </p>
          <button onClick={onSwitchToLogin} className="btn-outline">
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-[440px]">
      <header className="flex flex-col items-center mb-8">
        <div className="text-center">
          <h2 className="font-headline font-bold text-3xl text-on-surface tracking-tight mb-2">
            Crea una cuenta
          </h2>
          <p className="text-on-surface-variant font-medium">
            Unete a nuestra plataforma
          </p>
        </div>
      </header>

      <div className="card">
        <form onSubmit={handleSubmit}>
          {/* Username Field */}
          <div className="form-group">
            <label className="form-label">Username *</label>
            <div className="input-wrapper">
              <span className="material-symbols-outlined input-icon">person</span>
              <input
                type="text"
                name="username"
                className="input-field"
                placeholder="username"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          {/* Email Field */}
          <div className="form-group">
            <label className="form-label">Email *</label>
            <div className="input-wrapper">
              <span className="material-symbols-outlined input-icon">mail</span>
              <input
                type="email"
                name="email"
                className="input-field"
                placeholder="name@company.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          {/* Full Name Field */}
          <div className="form-group">
            <label className="form-label">Full Name (Optional)</label>
            <div className="input-wrapper">
              <span className="material-symbols-outlined input-icon">badge</span>
              <input
                type="text"
                name="full_name"
                className="input-field"
                placeholder="Your full name"
                value={formData.full_name}
                onChange={handleChange}
              />
            </div>
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label className="form-label">Password *</label>
            <div className="input-wrapper">
              <span className="material-symbols-outlined input-icon">lock</span>
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                className="input-field"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
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
              Crear Cuenta
              <span className="material-symbols-outlined text-lg">arrow_forward</span>
            </button>
          </div>
        </form>

        <div className="divider">
          <p className="text-sm text-on-surface-variant font-medium">
            Already have an account?
          </p>
          <button onClick={onSwitchToLogin} className="btn-outline">
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
};

export default Register;