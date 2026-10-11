import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/axiosConfig';
import { AuthContext } from '../context/AuthContext';
import { Heart, Mail, Lock, Eye, EyeOff } from 'lucide-react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await api.post('/auth/login/', { username, password });
      localStorage.setItem('access', response.data.access);
      localStorage.setItem('refresh', response.data.refresh);
      const loggedInUser = await login();
      if (!loggedInUser) {
        throw new Error('Unable to load the authenticated user profile.');
      }
      navigate(loggedInUser?.role === 'patient' ? '/patient/dashboard' : '/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      let errorMessage = 'Invalid username or password.';
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.non_field_errors) {
        errorMessage = err.response.data.non_field_errors.join(' ');
      } else if (err.request) {
        errorMessage = 'Cannot connect to server. Please check your network.';
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => setShowPassword(!showPassword);

  return (
    <div
      className="min-vh-100 d-flex align-items-center justify-content-center login-dark"
      style={{ background: 'var(--bg-body)' }}
    >
      <div className="auth-card">
        <div className="auth-logo">
          <Heart size={28} className="text-white" />
        </div>
        <h2 className="auth-title">VitalTrack</h2>
        <p className="auth-subtitle">Hypertension Monitoring System</p>

        <form onSubmit={handleSubmit} className="mt-4">
          <div className="mb-3">
            <label className="form-label small text-uppercase fw-semibold text-muted">Username</label>
            <div className="auth-input-group">
              <Mail size={16} className="input-icon" />
              <input
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="mb-3">
            <label className="form-label small text-uppercase fw-semibold text-muted">Password</label>
            <div className="auth-input-group">
              <Lock size={16} className="input-icon" />
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="btn btn-sm btn-link p-0 ms-2 text-muted"
                onClick={togglePasswordVisibility}
                tabIndex="-1"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <div className="text-end mb-2">
            <Link to="/forgot-password" className="small text-muted">Forgot password?</Link>
          </div>

          {error && <div className="alert alert-danger py-2 small">{error}</div>}

          <button
            type="submit"
            className="btn btn-primary w-100 py-2 fw-semibold"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Log in'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;