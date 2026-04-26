import React, { useState, useEffect } from 'react';
import WeightSliders from './WeightSliders';

const ProfileForm = ({ initialData, onSubmit, onCancel, isLoading }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    business_type: 'retail',
    weights: {
      population: 25,
      income: 25,
      education: 25,
      competition: 25
    }
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || '',
        description: initialData.description || '',
        business_type: initialData.target_business_type || 'retail',
        weights: initialData.weights || {
          population: 25,
          income: 25,
          education: 25,
          competition: 25
        }
      });
    }
  }, [initialData]);

  const validate = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es requerido';
    } else if (formData.name.length < 3) {
      newErrors.name = 'Mínimo 3 caracteres';
    }

    if (!formData.business_type.trim()) {
      newErrors.business_type = 'El tipo de negocio es requerido';
    }

    const total = Object.values(formData.weights).reduce((sum, w) => sum + w, 0);
    if (Math.abs(total - 100) > 0.01) {
      newErrors.weights = 'Los pesos deben sumar 100%';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  const handleWeightsChange = (newWeights) => {
    setFormData({ ...formData, weights: newWeights });
  };

  return (
    <form onSubmit={handleSubmit} className="profile-form">
      <div className="form-group">
        <label className="form-label">Nombre del Perfil *</label>
        <input
          type="text"
          className={`form-input ${errors.name ? 'error' : ''}`}
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="Ej: Perfil Retail"
          disabled={isLoading}
        />
        {errors.name && <span className="error-text">{errors.name}</span>}
      </div>

      <div className="form-group">
        <label className="form-label">Descripción</label>
        <textarea
          className="form-input"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Describe el propósito de este perfil..."
          rows="3"
          disabled={isLoading}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Tipo de Negocio *</label>
        <select
          className={`form-input ${errors.business_type ? 'error' : ''}`}
          value={formData.business_type}
          onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
          disabled={isLoading}
        >
          <option value="retail">Retail / Comercio</option>
          <option value="restaurant">Restaurante / Gastronomía</option>
          <option value="services">Servicios Profesionales</option>
          <option value="entertainment">Entretenimiento</option>
          <option value="education">Educación</option>
          <option value="health">Salud</option>
        </select>
        {errors.business_type && <span className="error-text">{errors.business_type}</span>}
      </div>

      <div className="form-group">
        <label className="form-label">Pesos de Variables *</label>
        <WeightSliders
          weights={formData.weights}
          onChange={handleWeightsChange}
          disabled={isLoading}
        />
        {errors.weights && <span className="error-text">{errors.weights}</span>}
      </div>

      <div className="form-actions">
        <button type="button" className="btn-outline" onClick={onCancel} disabled={isLoading}>
          Cancelar
        </button>
        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Guardando...
            </>
          ) : (
            <>
              {initialData ? 'Actualizar' : 'Crear'} Perfil
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default ProfileForm;