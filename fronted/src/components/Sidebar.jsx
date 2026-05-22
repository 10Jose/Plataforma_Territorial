import React, { useState } from 'react';
import '../styles/Sidebar.css';

const Sidebar = ({ activeTab, onTabChange, onLogout }) => {
  const [showAccountMenu, setShowAccountMenu] = useState(false);
  const [collapsed, setCollapsed] = useState(true);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'dashboard' },
    { id: 'indicators', label: 'Indicadores', icon: 'analytics' },
    { id: 'configuration', label: 'Configuración', icon: 'tune' },
    { id: 'scoring', label: 'Scoring', icon: 'score' },
    { id: 'ranking', label: 'Ranking', icon: 'leaderboard' },
    { id: 'comparison', label: 'Comparación', icon: 'compare' },
    { id: 'ml', label: 'Predicción ML', icon: 'query_stats' },
    { id: 'recommendations', label: 'Recomendaciones', icon: 'lightbulb' },
    { id: 'audit', label: 'Auditoría', icon: 'history' },
  ];

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}
        onMouseEnter={() => setCollapsed(false)}
        onMouseLeave={() => setCollapsed(true)}
    >
          {/* Logo */}
          <div className="sidebar-brand">
            <div className="brand-icon">
              <span className="material-symbols-outlined">analytics</span>
            </div>
            {!collapsed && (
              <div>
                <h3 className="brand-name">Plataforma Territorial</h3>
                <p className="brand-subtitle">Analítica Inteligente</p>
              </div>
            )}
          </div>

          {/* Navigation */}
          <nav className="sidebar-nav">
            {menuItems.map(item => (
              <button
                key={item.id}
                className={`sidebar-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => onTabChange(item.id)}
                title={collapsed ? item.label : ''}
              >
                <span className="material-symbols-outlined">{item.icon}</span>
                {!collapsed && <span className="sidebar-label">{item.label}</span>}
              </button>
            ))}
          </nav>

          {/* Bottom Section */}
          <div className="sidebar-footer">
            <button
              className="sidebar-item account-btn"
              onClick={() => !collapsed && setShowAccountMenu(!showAccountMenu)}
              title={collapsed ? 'Cuenta' : ''}
            >
              <span className="material-symbols-outlined">person</span>
              {!collapsed && (
                <>
                  <span className="sidebar-label">Cuenta</span>
                  <span className="material-symbols-outlined account-arrow" style={{
                    transform: showAccountMenu ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.2s',
                    fontSize: '1rem'
                  }}>
                    expand_more
                  </span>
                </>
              )}
            </button>

            {/* Account Menu Dropdown */}
            {!collapsed && showAccountMenu && (
              <div className="account-menu">
                <button className="account-menu-item" onClick={onLogout}>
                  <span className="material-symbols-outlined">logout</span>
                  <span>Cerrar Sesión</span>
                </button>
              </div>
            )}
          </div>
        </aside>
      );
    };

    export default Sidebar;