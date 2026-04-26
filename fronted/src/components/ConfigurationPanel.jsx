import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import ProfileForm from './ProfileForm';
import '../styles/configuration.css';

const ConfigurationPanel = () => {
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    setLoading(true);
    try {
      const data = await api.getProfiles();
      setProfiles(data);
      const active = data.find(p => p.is_active);
      if (active) setSelectedProfile(active);
    } catch (err) {
      setError('Error al cargar perfiles: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProfile = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const newProfile = await api.createProfile({
        name: formData.name,
        description: formData.description,
        business_type: formData.business_type,
        weights: formData.weights
      });
      setProfiles([...profiles, newProfile]);
      setIsCreating(false);
      showSuccessMessage('Perfil creado exitosamente');
    } catch (err) {
      setError('Error al crear perfil: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const updatedProfile = await api.updateProfile(selectedProfile.id, {
        name: formData.name,
        description: formData.description,
        business_type: formData.business_type,
        weights: formData.weights
      });
      setProfiles(profiles.map(p => p.id === updatedProfile.id ? updatedProfile : p));
      setIsEditing(false);
      if (selectedProfile?.id === updatedProfile.id) {
        setSelectedProfile(updatedProfile);
      }
      showSuccessMessage('Perfil actualizado exitosamente');
    } catch (err) {
      setError('Error al actualizar perfil: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleActivateProfile = async (profileId) => {
    setLoading(true);
    try {
      const activatedProfile = await api.activateProfile(profileId);
      setProfiles(profiles.map(p => ({
        ...p,
        is_active: p.id === activatedProfile.id
      })));
      setSelectedProfile(activatedProfile);
      showSuccessMessage(`Perfil "${activatedProfile.name}" activado`);
    } catch (err) {
      setError('Error al activar perfil: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProfile = async (profileId, profileName) => {
    if (!window.confirm(`¿Eliminar el perfil "${profileName}"?`)) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await api.deleteProfile(profileId);
      setProfiles(profiles.filter(p => p.id !== profileId));
      if (selectedProfile?.id === profileId) {
        const active = profiles.find(p => p.is_active && p.id !== profileId);
        setSelectedProfile(active || profiles.find(p => p.id !== profileId) || null);
      }
      showSuccessMessage(`Perfil "${profileName}" eliminado`);
    } catch (err) {
      if (err.message.includes('400') || err.message.includes('No se puede eliminar el perfil activo')) {
        setError('No se puede eliminar el perfil activo. Activa otro perfil primero.');
      } else {
        setError('Error al eliminar perfil: ' + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const showSuccessMessage = (message) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  const getIconForType = (type) => {
    const icons = {
      retail: 'shopping_cart',
      restaurant: 'restaurant',
      services: 'business_center',
      entertainment: 'theaters',
      education: 'school',
      health: 'local_hospital'
    };
    return icons[type] || 'dataset';
  };

  const formatRelativeTime = (dateString) => {
    if (!dateString) return '';

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffMinutes < 1) {
      return 'Actualizado hace un momento';
    }

    if (diffMinutes < 60) {
      return `Actualizado hace ${diffMinutes} ${diffMinutes === 1 ? 'minuto' : 'minutos'}`;
    }

    if (diffHours < 24) {
      const remainingMinutes = diffMinutes % 60;

      if (remainingMinutes === 0) {
        return `Actualizado hace ${diffHours} ${diffHours === 1 ? 'hora' : 'horas'}`;
      }

      return `Actualizado hace ${diffHours} ${diffHours === 1 ? 'hora' : 'horas'} y ${remainingMinutes} ${remainingMinutes === 1 ? 'minuto' : 'minutos'}`;
    }

    return `Actualizado el ${date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: now.getFullYear() !== date.getFullYear() ? 'numeric' : undefined
    })}`;
  };

  if (loading && profiles.length === 0) {
    return (
      <div className="loading-container">
        <div className="spinner-large"></div>
        <p>Cargando configuración...</p>
      </div>
    );
  }

  return (
    <div className="config-panel">
      {/* Header */}
      <div className="config-header">
        <div className="config-title-section">
          <h1 className="config-title">Configuración de Scoring</h1>
          <p className="config-subtitle">
            Administre y ajuste los perfiles analíticos para el cálculo de potencial territorial.
            Defina los pesos de cada variable para adaptar el scoring a sus necesidades estratégicas.
          </p>
        </div>
        {!isCreating && !isEditing && (
          <button className="btn-new-profile" onClick={() => setIsCreating(true)}>
            <span className="material-symbols-outlined">add</span>
            Nuevo Perfil
          </button>
        )}
      </div>

      {/* Messages */}
      {successMessage && (
        <div className="success-message">
          <span className="material-symbols-outlined">check_circle</span>
          {successMessage}
        </div>
      )}
      {error && (
        <div className="error-message">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}

      {/* Formularios */}
      {isCreating && (
        <div className="form-section">
          <h2>Crear Nuevo Perfil</h2>
          <ProfileForm
            onSubmit={handleCreateProfile}
            onCancel={() => setIsCreating(false)}
            isLoading={loading}
          />
        </div>
      )}

      {isEditing && selectedProfile && (
        <div className="form-section">
          <h2>Editar Perfil: {selectedProfile.name}</h2>
          <ProfileForm
            initialData={selectedProfile}
            onSubmit={handleUpdateProfile}
            onCancel={() => setIsEditing(false)}
            isLoading={loading}
          />
        </div>
      )}

      {/* Vista Principal */}
      {!isCreating && !isEditing && (
        <div className="config-grid">
          {/* Left: Active Profile */}
          <div className="config-left">
            {selectedProfile ? (
              <div className="active-profile-card">
                <div className="active-profile-header">
                  <div>
                    <span className="active-profile-label">Perfil Seleccionado</span>
                    <h2 className="active-profile-name">{selectedProfile.name}</h2>
                  </div>
                  <span className="active-badge">ACTIVO</span>
                </div>

                <div className="weights-grid">
                  {[
                    { key: 'population', label: 'Población' },
                    { key: 'income', label: 'Ingreso' },
                    { key: 'education', label: 'Educación' },
                    { key: 'competition', label: 'Competencia' }
                  ].map(({ key, label }) => {
                    const value = selectedProfile.weights[key] || 0;
                    return (
                      <div key={key} className="weight-card">
                        <div className="weight-header">
                          <span className="weight-label">{label}</span>
                          <span className="weight-value">{value}%</span>
                        </div>
                        <div className="weight-bar-container">
                          <div className="weight-bar" style={{ width: `${value}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="active-profile-actions">
                  <button className="btn-delete" onClick={() => handleDeleteProfile(selectedProfile.id, selectedProfile.name)}>
                    <span className="material-symbols-outlined">delete</span>
                    Eliminar Perfil
                  </button>
                  <button className="btn-edit" onClick={() => setIsEditing(true)}>
                    Editar Pesos
                  </button>
                </div>
              </div>
            ) : (
              <div className="empty-active-profile">
                <span className="material-symbols-outlined">analytics</span>
                <h3>No hay perfil activo</h3>
                <p>Selecciona o crea un perfil para ver sus detalles.</p>
              </div>
            )}

            <div className="info-box">
              <span className="material-symbols-outlined">analytics</span>
              <p>Los cambios en los pesos afectarán los cálculos de Scoring en tiempo real para todos los territorios visualizados.</p>
            </div>
          </div>

          {/* Right: Profiles List */}
          <div className="config-right">
            <div className="profiles-header">
              <h3>Perfiles Configurados
                  <span className="tooltip-wrapper">
                      <span className="material-symbols-outlined tooltip-icon">help</span>
                      <span className="tooltip-content">Los perfiles definen los pesos de cada variable.<br/>
                          La suma de pesos debe ser 100%.
                      </span>
                    </span>
                  </h3>
              <span className="profiles-count">{profiles.length} TOTAL</span>
            </div>

            <div className="profiles-list">
              {profiles.length === 0 ? (
                <div className="empty-profiles">
                  <span className="material-symbols-outlined">settings</span>
                  <p>No hay perfiles configurados</p>
                  <p className="hint">Crea tu primer perfil para comenzar</p>
                </div>
              ) : (
                profiles.map((profile) => (
                  <div
                    key={profile.id}
                    className={`profile-item ${selectedProfile?.id === profile.id ? 'selected' : ''}`}
                    onClick={() => setSelectedProfile(profile)}
                  >
                    <div className="profile-item-content">
                      <div className={`profile-icon ${selectedProfile?.id === profile.id ? 'active-icon' : ''}`}>
                        <span className="material-symbols-outlined">
                          {getIconForType(profile.target_business_type)}
                        </span>
                      </div>
                      <div className="profile-info">
                        <h4>{profile.name}</h4>
                        <p>{formatRelativeTime(profile.created_at)}</p>
                      </div>
                    </div>
                    <div className="profile-item-actions">
                      {!profile.is_active && (
                        <>
                          <button
                            className="icon-btn"
                            onClick={(e) => { e.stopPropagation(); handleActivateProfile(profile.id); }}
                            title="Activar"
                          >
                            <span className="material-symbols-outlined">play_arrow</span>
                          </button>
                          <button
                            className="icon-btn"
                            onClick={(e) => { e.stopPropagation(); setSelectedProfile(profile); setIsEditing(true); }}
                            title="Editar"
                          >
                            <span className="material-symbols-outlined">edit</span>
                          </button>
                          <button
                            className="icon-btn delete"
                            onClick={(e) => { e.stopPropagation(); handleDeleteProfile(profile.id, profile.name); }}
                            title="Eliminar"
                          >
                            <span className="material-symbols-outlined">delete</span>
                          </button>
                        </>
                      )}
                      {profile.is_active && (
                        <>
                          <button
                            className="icon-btn delete"
                            onClick={(e) => { e.stopPropagation(); handleDeleteProfile(profile.id, profile.name); }}
                            title="Eliminar"
                          >
                            <span className="material-symbols-outlined">delete</span>
                          </button>
                          <span className="material-symbols-outlined check-icon">check_circle</span>
                        </>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfigurationPanel;