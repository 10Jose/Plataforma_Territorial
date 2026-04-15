import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { validatePassword, getStrengthColor, getStrengthLabel } from '../utils/passwordValidator';
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
  const [passwordValidation, setPasswordValidation] = useState(null);
  const [confirmPassword, setConfirmPassword] = useState('');
  const [touched, setTouched] = useState({ password: false, confirm: false });
  const { register, error } = useAuth();

  // Validar contraseña en tiempo real
  useEffect(() => {
    if (formData.password) {
      const validation = validatePassword(formData.password);
      setPasswordValidation(validation);
    } else {
      setPasswordValidation(null);
    }
  }, [formData.password]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const isPasswordValid = () => {
    return passwordValidation?.isValid || false;
  };

  const doPasswordsMatch = () => {
    return formData.password && confirmPassword && formData.password === confirmPassword;
  };

  const isFormValid = () => {
    return formData.username.length >= 3 &&
           formData.email.includes('@') &&
           formData.email.includes('.') &&
           isPasswordValid() &&
           doPasswordsMatch();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!isFormValid()) {
      setTouched({ password: true, confirm: true });
      return;
    }

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
                minLength={3}
              />
            </div>
            {formData.username && formData.username.length < 3 && (
              <p className="text-error text-xs mt-1">Mínimo 3 caracteres</p>
            )}
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
                onBlur={() => setTouched({ ...touched, password: true })}
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

            {/* Password Strength Indicator */}
            {formData.password && (
              <div className="mt-2">
                <div className="flex items-center gap-2 mb-1">
                  <div className="h-1.5 flex-1 rounded-full bg-gray-200 overflow-hidden">
                    <div
                      className="h-full transition-all duration-300"
                      style={{
                        width: `${passwordValidation?.strength || 0}%`,
                        backgroundColor: getStrengthColor(passwordValidation?.strength || 0)
                      }}
                    />
                  </div>
                  <span
                    className="text-xs font-medium"
                    style={{ color: getStrengthColor(passwordValidation?.strength || 0) }}
                  >
                    {getStrengthLabel(passwordValidation?.strength || 0)}
                  </span>
                </div>

                {/* Validation Checklist */}
                {touched.password && passwordValidation && (
                  <div className="validation-checklist">
                    <CheckItem
                      passed={passwordValidation.checks.minLength}
                      label="8+ caracteres"
                    />
                    <CheckItem
                      passed={passwordValidation.checks.hasUpperCase}
                      label="Una mayúscula"
                    />
                    <CheckItem
                      passed={passwordValidation.checks.hasLowerCase}
                      label="Una minúscula"
                    />
                    <CheckItem
                      passed={passwordValidation.checks.hasNumber}
                      label="Un número"
                    />
                    <CheckItem
                      passed={passwordValidation.checks.hasSpecial}
                      label="Un carácter especial"
                    />
                    <CheckItem
                      passed={passwordValidation.checks.noSequences}
                      label="Sin secuencias"
                    />
                    <CheckItem
                      passed={passwordValidation.checks.noRepetition}
                      label="Sin repeticiones"
                    />
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Confirm Password Field */}
          <div className="form-group">
            <label className="form-label">Confirmar Contraseña *</label>
            <div className="input-wrapper">
              <span className="material-symbols-outlined input-icon">lock</span>
              <input
                type={showPassword ? 'text' : 'password'}
                className="input-field"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                onBlur={() => setTouched({ ...touched, confirm: true })}
                required
              />
            </div>
            {touched.confirm && confirmPassword && !doPasswordsMatch() && (
              <p className="text-error text-xs mt-1">Las contraseñas no coinciden</p>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <div className="pt-2">
            <button
              type="submit"
              className="btn-primary"
              disabled={isLoading || (touched.password && !isFormValid())}
            >
              {isLoading ? <div className="spinner"></div> : null}
              Crear Cuenta
              <span className="material-symbols-outlined text-lg">arrow_forward</span>
            </button>
          </div>
        </form>

        <div className="divider">
          <p className="text-sm text-on-surface-variant font-medium">
            Ya tienes una cuenta?
          </p>
          <button onClick={onSwitchToLogin} className="btn-outline">
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
};

// Componente auxiliar para items de validación
const CheckItem = ({ passed, label }) => (
  <div className={`check-item ${passed ? 'passed' : 'failed'}`}>
    <span className="material-symbols-outlined text-sm">
      {passed ? 'check_circle' : 'cancel'}
    </span>
    <span>{label}</span>
  </div>
);

export default Register;