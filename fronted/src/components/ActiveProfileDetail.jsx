import React from 'react';

const weightConfigs = [
  { key: 'population', label: 'POBLACIÓN', color: 'bg-blue-500' },
  { key: 'income', label: 'INGRESO', color: 'bg-green-500' },
  { key: 'education', label: 'EDUCACIÓN', color: 'bg-purple-500' },
  { key: 'competition', label: 'COMPETENCIA', color: 'bg-orange-500' }
];

const ActiveProfileCompact = ({ profile, onEdit, onDelete }) => {
  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-start mb-5">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded">
            ACTIVO
          </span>
          <h3 className="font-medium text-gray-900">{profile.name}</h3>
        </div>
        <div className="flex gap-1">
          <button
            onClick={onEdit}
            className="px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
          >
            Editar Perfil
          </button>
          <button
            onClick={onDelete}
            className="px-3 py-1.5 text-xs font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
          >
            Eliminar
          </button>
        </div>
      </div>

      {/* Weight Bars */}
      <div className="space-y-4">
        {weightConfigs.map((config) => {
          const value = profile.weights[config.key] || 0;
          return (
            <div key={config.key}>
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-medium text-gray-500">{config.label}</span>
                <span className="text-sm font-semibold text-gray-900">{value}%</span>
              </div>
              <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                <div
                  className={`${config.color} h-full rounded-full transition-all duration-300`}
                  style={{ width: `${value}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Description */}
      {profile.description && (
        <div className="mt-5 pt-4 border-t border-gray-100">
          <p className="text-xs text-gray-400">{profile.description}</p>
        </div>
      )}
    </div>
  );
};

export default ActiveProfileCompact;