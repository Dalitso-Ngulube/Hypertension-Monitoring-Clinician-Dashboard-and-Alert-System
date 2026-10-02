import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { User, Bell, Shield, Moon, Sun, Save, Mail, Phone } from 'lucide-react';

const Settings = () => {
  const { user } = useContext(AuthContext);
  const { darkMode, toggleDarkMode } = useTheme();
  const [saved, setSaved] = useState(false);
  const [profile, setProfile] = useState({
    username: user?.username || '',
    email: user?.email || '',
    phone: user?.phone_number || '',
  });

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="container-fluid py-4">
      <h1 className="sidebar-page-heading fw-bold">Settings</h1>
      <p className="text-muted small mb-4">Configure your account and application preferences</p>

      <div className="row g-4">
        <div className="col-lg-6">
          <div className="card card-clinical">
            <div className="card-header"><User size={16} className="me-2" /> Profile Settings</div>
            <div className="card-body">
              <form onSubmit={handleSave}>
                <div className="mb-3">
                  <label className="form-label small fw-semibold text-muted text-uppercase">Username</label>
                  <div className="auth-input-group">
                    <User size={16} className="input-icon" />
                    <input type="text" value={profile.username} onChange={(e) => setProfile({ ...profile, username: e.target.value })} />
                  </div>
                </div>
                <div className="mb-3">
                  <label className="form-label small fw-semibold text-muted text-uppercase">Email</label>
                  <div className="auth-input-group">
                    <Mail size={16} className="input-icon" />
                    <input type="email" value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })} />
                  </div>
                </div>
                <div className="mb-3">
                  <label className="form-label small fw-semibold text-muted text-uppercase">Phone Number</label>
                  <div className="auth-input-group">
                    <Phone size={16} className="input-icon" />
                    <input type="text" value={profile.phone} onChange={(e) => setProfile({ ...profile, phone: e.target.value })} />
                  </div>
                </div>
                <button type="submit" className="btn btn-primary w-100"><Save size={16} className="me-1" /> Save Changes</button>
                {saved && <div className="alert alert-success mt-2 py-1 small">Settings saved successfully!</div>}
              </form>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card card-clinical mb-3">
            <div className="card-header">Appearance</div>
            <div className="card-body d-flex justify-content-between align-items-center">
              <div>
                <p className="fw-semibold mb-0">Theme</p>
                <p className="small text-muted mb-0">Switch between light and dark mode</p>
              </div>
              <button className="btn btn-outline-secondary" onClick={toggleDarkMode}>
                {darkMode ? <Sun size={18} className="me-1" /> : <Moon size={18} className="me-1" />}
                {darkMode ? 'Light' : 'Dark'}
              </button>
            </div>
          </div>

          <div className="card card-clinical mb-3">
            <div className="card-header"><Bell size={16} className="me-2" /> Notifications</div>
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center border-bottom pb-2 mb-2">
                <div><p className="fw-semibold mb-0">Email Alerts</p><p className="small text-muted">Receive critical alerts via email</p></div>
                <div className="form-check form-switch"><input className="form-check-input" type="checkbox" defaultChecked /></div>
              </div>
              <div className="d-flex justify-content-between align-items-center">
                <div><p className="fw-semibold mb-0">SMS Alerts</p><p className="small text-muted">Receive critical alerts via SMS</p></div>
                <div className="form-check form-switch"><input className="form-check-input" type="checkbox" /></div>
              </div>
            </div>
          </div>

          <div className="card card-clinical">
            <div className="card-header"><Shield size={16} className="me-2" /> Security</div>
            <div className="card-body">
              <button className="btn btn-outline-secondary w-100">Change Password</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;