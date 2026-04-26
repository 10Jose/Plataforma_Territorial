import React from 'react';

const ProfileListCompact = ({ profiles, selectedId, onSelect, onActivate, onEdit, onDelete }) => {
  const formatRelativeTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffHours = Math.floor((now - date) / (1000 * 60 * 60));

    if (diffHours < 24) {
      return `Actualizado hace ${diffHours} horas`;
    } else if (diffHours < 48) {
      return 'Actualizado ayer';
    } else {
      return `Actualizado el ${date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}`;
    }
  };

  if (profiles.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400 text-sm">
        <span className="material-symbols-outlined text-3xl mb-2">settings</span>
        <p>No hay perfiles configurados</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {profiles.map((profile) => (
        <div
          key={profile.id}
          className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
            selectedId === profile.id
              ? 'bg-blue-50 border border-blue-200'
              : 'hover:bg-gray-50 border border-transparent'
          }`}
          onClick={() => onSelect(profile)}
        >
          <div className="flex items-center gap-3 flex-1">
            <div className={`w-2 h-2 rounded-full ${profile.is_active ? 'bg-green-500' : 'bg-gray-300'}`} />
            <div>
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-900">{profile.name}</span>
                {profile.is_active && (
                  <span className="text-[10px] font-bold text-green-600 bg-green-50 px-1.5 py-0.5 rounded">
                    ACTIVO
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-400">{formatRelativeTime(profile.created_at)}</p>
            </div>
          </div>

          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity">
            {!profile.is_active && (
              <button
                onClick={(e) => { e.stopPropagation(); onActivate(profile.id); }}
                className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded"
                title="Activar"
              >
                <span className="material-symbols-outlined text-base">play_arrow</span>
              </button>
            )}
            <button
              onClick={(e) => { e.stopPropagation(); onEdit(profile); }}
              className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
              title="Editar"
            >
              <span className="material-symbols-outlined text-base">edit</span>
            </button>
            {!profile.is_active && (
              <button
                onClick={(e) => { e.stopPropagation(); onDelete(profile.id, profile.name); }}
                className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                title="Eliminar"
              >
                <span className="material-symbols-outlined text-base">delete</span>
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ProfileListCompact;