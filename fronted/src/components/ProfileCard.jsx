import React from 'react';

const ProfileCard = ({ profile, isActive, onSelect, onEdit, onActivate, onDelete }) => {
  const getBusinessTypeIcon = (type) => {
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

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
  };

  return (
    <div
      className={`group bg-surface-container-lowest p-5 rounded-2xl border transition-all shadow-sm cursor-pointer ${
        isActive
          ? 'border-2 border-primary ring-4 ring-primary/5'
          : 'border-outline-variant/10 hover:border-primary/30 hover:shadow-md'
      }`}
      onClick={onSelect}
    >
      <div className="flex justify-between items-start">
        <div className="flex gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${
            isActive
              ? 'bg-primary/10 text-primary'
              : 'bg-surface-container-low text-on-surface-variant group-hover:bg-primary-container/20 group-hover:text-primary'
          }`}>
            <span className="material-symbols-outlined" style={isActive ? { fontVariationSettings: '"FILL" 1' } : {}}>
              {getBusinessTypeIcon(profile.target_business_type)}
            </span>
          </div>
          <div>
            <h4 className="font-headline font-bold text-on-surface">{profile.name}</h4>
            <p className="label-font text-xs text-on-surface-variant tracking-wide">
              Actualizado {formatDate(profile.created_at)}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {!isActive && (
            <>
              <button
                className="material-symbols-outlined text-on-surface-variant hover:text-primary p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => { e.stopPropagation(); onActivate(); }}
                title="Activar"
              >
                play_arrow
              </button>
              <button
                className="material-symbols-outlined text-on-surface-variant hover:text-primary p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => { e.stopPropagation(); onEdit(); }}
                title="Editar"
              >
                edit
              </button>
              <button
                className="material-symbols-outlined text-on-surface-variant hover:text-error p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => { e.stopPropagation(); onDelete(); }}
                title="Eliminar"
              >
                delete
              </button>
            </>
          )}
          {isActive && (
            <>
              <button
                className="material-symbols-outlined text-on-surface-variant hover:text-error p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => { e.stopPropagation(); onDelete(); }}
                title="Eliminar"
              >
                delete
              </button>
              <span
                className="material-symbols-outlined text-primary"
                style={{ fontVariationSettings: '"FILL" 1' }}
              >
                check_circle
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileCard;