import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip
} from 'recharts';
import '../styles/RadarChart.css';

const RadarChartComponent = ({ data, zoneName }) => {
  if (!data) {
    return (
      <div className="radar-empty">
        <span className="material-symbols-outlined">analytics</span>
        <p>Selecciona una zona para ver el gráfico de radar</p>
      </div>
    );
  }

  const contributions = data.contributions || {};

  // Normalizar contribuciones a 0-1
  const maxContribution = Math.max(
    contributions.population || 0,
    contributions.income || 0,
    contributions.education || 0,
    contributions.competition_penalty || 0,
    1
  );

  const chartData = [
    {
      variable: 'Población',
      value: (contributions.population || 0) / maxContribution,
      original: contributions.population || 0
    },
    {
      variable: 'Ingreso',
      value: (contributions.income || 0) / maxContribution,
      original: contributions.income || 0
    },
    {
      variable: 'Educación',
      value: (contributions.education || 0) / maxContribution,
      original: contributions.education || 0
    },
    {
      variable: 'Competencia',
      value: 1 - ((contributions.competition_penalty || 0) / maxContribution),
      original: contributions.competition_penalty || 0
    },
  ];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      const percentage = (item.value * 100).toFixed(1);
      const originalValue = item.original.toFixed(1);

      return (
        <div className="radar-tooltip">
          <p className="tooltip-variable">{item.variable}</p>
          <p className="tooltip-value">{percentage}%</p>
          <p className="tooltip-hint">
            Contribución original: {originalValue}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="radar-container">
      <div className="radar-header">
        <h3 className="radar-title">
          Perfil de Zona: <span>{zoneName}</span>
        </h3>
        <span className="material-symbols-outlined help-icon" title="Valores normalizados respecto a la contribución máxima de esta zona. Competencia se invierte: menos penalización = mejor.">
          help
        </span>
      </div>
      <div className="radar-chart-wrapper">
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis
              dataKey="variable"
              tick={{ fill: '#64748b', fontSize: 12, fontWeight: 500 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 1]}
              tick={{ fill: '#94a3b8', fontSize: 10 }}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            />
            <Radar
              name="Valor"
              dataKey="value"
              stroke="#006944"
              fill="#006944"
              fillOpacity={0.3}
              strokeWidth={2}
            />
            <Tooltip content={<CustomTooltip />} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="radar-legend">
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#006944' }}></span>
          <span>Valor normalizado (0-100%)</span>
        </div>
        <div className="legend-note">
          <span className="material-symbols-outlined">info</span>
          <span>Población, Ingreso, Educación: + grande = mejor (más cerca del borde)
              Competencia: + grande = peor  (más cerca del centro)
              </span>
        </div>
      </div>
    </div>
  );
};

export default RadarChartComponent;