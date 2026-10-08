import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Settings,
  LogOut,
  Sun,
  Moon,
  Menu,
  X,
  HeartPulse,
  Calendar,
} from 'lucide-react';

const PatientSidebar = ({ collapsed, toggleSidebar }) => {
  const { logout, user } = useContext(AuthContext);
  const { darkMode, toggleDarkMode } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };
  const initials = user?.username?.charAt(0).toUpperCase() || '?';

  return (
    <>
      <button
        onClick={toggleSidebar}
        className={`btn btn-light position-fixed top-0 start-0 m-2 z-3 shadow-sm rounded-circle p-2 border-0 sidebar-toggle-btn ${
          collapsed ? 'sidebar-toggle-btn--collapsed' : 'sidebar-toggle-btn--open'
        }`}
        aria-label={collapsed ? 'Open sidebar' : 'Close sidebar'}
        title={collapsed ? 'Open sidebar' : 'Close sidebar'}
      >
        {collapsed ? <Menu size={20} /> : <X size={20} />}
      </button>

      <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
        <div className="brand">
          <span className="logo-mark">V</span>
          <span className="logo-text">{collapsed ? '' : 'VitalTrack'}</span>
        </div>

        <nav className="nav flex-column px-2">
          <NavLink
            to="/patient/dashboard"
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <span className="nav-icon">
              <HeartPulse size={18} strokeWidth={1.75} />
            </span>
            {!collapsed && 'My Health'}
          </NavLink>

          <NavLink
            to="/appointments"
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <span className="nav-icon">
              <Calendar size={18} strokeWidth={1.75} />
            </span>
            {!collapsed && 'Appointments'}
          </NavLink>

          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <span className="nav-icon">
              <Settings size={18} strokeWidth={1.75} />
            </span>
            {!collapsed && 'Settings'}
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className="d-flex align-items-center gap-2">
            <div className="user-avatar">{initials}</div>
            <div>
              <div className="user-name">{user?.username}</div>
              <div className="user-role">{user?.role}</div>
            </div>
          </div>
          <button className="btn-theme-toggle mt-2" onClick={toggleDarkMode}>
            {darkMode ? (
              <Sun size={14} className="me-1" />
            ) : (
              <Moon size={14} className="me-1" />
            )}
            {darkMode ? 'Light' : 'Dark'}
          </button>
          <button className="btn-logout mt-1" onClick={handleLogout}>
            <LogOut size={14} className="me-1" /> Logout
          </button>
        </div>
      </div>
    </>
  );
};

export default PatientSidebar;