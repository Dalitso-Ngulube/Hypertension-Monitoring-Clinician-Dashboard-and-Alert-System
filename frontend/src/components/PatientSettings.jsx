import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Save, User, Mail, Phone, Moon, Sun } from 'lucide-react';

const PatientSettings = () => {
  const { user } = useContext(AuthContext);
  const { darkMode, toggleDarkMode } = useTheme();
  const [profile, setProfile] = useState({
    username: user?.username || '',
    email: user?.email || '',
    phone: user?.phone_number || '',
  });
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="mt-2">
      <form onSubmit={handleSave}>
        <div className="mb-3">
          <label className="form-label small fw-semibold text-muted text-uppercase">
            <User size={14} className="me-1" /> Username
          </label>
          <input
            type="text"
            className="form-control form-control-sm"
            value={profile.username}
            onChange={(e) => setProfile({ ...profile, username: e.target.value })}
          />
        </div>
        <div className="mb-3">
          <label className="form-label small fw-semibold text-muted text-uppercase">
            <Mail size={14} className="me-1" /> Email
          </label>
          <input
            type="email"
            className="form-control form-control-sm"
            value={profile.email}
            onChange={(e) => setProfile({ ...profile, email: e.target.value })}
          />
        </div>
        <div className="mb-3">
          <label className="form-label small fw-semibold text-muted text-uppercase">
            <Phone size={14} className="me-1" /> Phone
          </label>
          <input
            type="text"
            className="form-control form-control-sm"
            value={profile.phone}
            onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
          />
        </div>
        <div className="mb-3 d-flex justify-content-between align-items-center">
          <div>
            <span className="small fw-semibold text-muted text-uppercase">Theme</span>
            <p className="small text-muted mb-0">{darkMode ? 'Dark' : 'Light'}</p>
          </div>
          <button
            type="button"
            className="btn btn-outline-secondary btn-sm"
            onClick={toggleDarkMode}
          >
            {darkMode ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
        <button type="submit" className="btn btn-primary btn-sm w-100">
          <Save size={14} className="me-1" /> Save Changes
        </button>
        {saved && (
          <div className="alert alert-success mt-2 py-1 small">Settings saved!</div>
        )}
      </form>
    </div>
  );
};

export default PatientSettings;