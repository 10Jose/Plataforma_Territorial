import React, { useState, useEffect } from 'react';

const WeightSliders = ({ weights, onChange, disabled = false }) => {
  const [localWeights, setLocalWeights] = useState(weights || {
    population: 25,
    income: 25,
    education: 25,
    competition: 25
  });

  useEffect(() => {
    if (weights) {
      setLocalWeights(weights);
    }
  }, [weights]);

  const total = Object.values(localWeights).reduce((sum, w) => sum + w, 0);
  const isValid = Math.abs(total - 100) < 0.01;

  const handleSliderChange = (name, value) => {
    const newWeights = { ...localWeights, [name]: value };
    setLocalWeights(newWeights);
    onChange(newWeights);
  };

  const configs = [
    { name: 'population', label: 'Población', icon: 'groups', color: '#3b82f6' },
    { name: 'income', label: 'Ingreso Promedio', icon: 'payments', color: '#10b981' },
    { name: 'education', label: 'Nivel Educativo', icon: 'school', color: '#8b5cf6' },
    { name: 'competition', label: 'Competencia', icon: 'storefront', color: '#ef4444' }
  ];

  return (
    <div className="weight-sliders">
      <div className="total-indicator">
        <div className="total-label">Total Pesos</div>
        <div className={`total-value ${isValid ? 'valid' : 'invalid'}`}>
          {total.toFixed(1)}%
        </div>
        {!isValid && (
          <div className="total-error">
            {total > 100 ? 'Excede 100%' : 'Faltan ' + (100 - total).toFixed(1) + '%'}
          </div>
        )}
      </div>

      {configs.map((config) => (
        <div key={config.name} className="slider-group">
          <div className="slider-header">
            <span className="slider-icon" style={{ color: config.color }}>
              <span className="material-symbols-outlined">{config.icon}</span>
            </span>
            <span className="slider-label">{config.label}</span>
            <span className="slider-value">{localWeights[config.name]}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="1"
            value={localWeights[config.name]}
            onChange={(e) => handleSliderChange(config.name, parseFloat(e.target.value))}
            disabled={disabled}
            className="slider"
            style={{ '--slider-color': config.color }}
          />
        </div>
      ))}
    </div>
  );
};

export default WeightSliders;