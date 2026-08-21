import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/axiosConfig';
import { Heart, Lock, Eye, EyeOff } from 'lucide-react';

const ResetPasswordConfirm = () => {
  const { uidb64, token } = useParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) { setError('Passwords do not match'); return; }
    if (password.length < 6) { setError('Password must be at least 6 characters'); return; }
    setLoading(true);
    setError('');
    try {
      await api.post(`/auth/password-reset/confirm/${uidb64}/${token}/`, { password });
      setSuccess(true);
      setTimeout(() => navigate('/'), 2000);
    } catch (err) {
      setError('Invalid or expired reset link. Please try again.');
    } finally { setLoading(false); }
  };

  if (success) {
    return (
      <div className="min-vh-100 d-flex align-items-center justify-content-center" style={{ background: 'var(--bg-body)' }}>
        <div className="auth-card text-center">
          <div className="text-5xl mb-3">✅</div>
          <h2 className="auth-title">Password Reset Complete</h2>
          <p className="auth-subtitle">Your password has been set. Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center" style={{ background: 'var(--bg-body)' }}>
      <div className="auth-card">
        <div className="auth-logo"><Heart size={28} className="text-white" /></div>
        <h2 className="auth-title">Set New Password</h2>
        <form onSubmit={handleSubmit} className="mt-4">
          <div className="mb-3">
            <label className="form-label small text-uppercase fw-semibold text-muted">New Password</label>
            <div className="auth-input-group">
              <Lock size={16} className="input-icon" />
              <input type={showPassword ? 'text' : 'password'} placeholder="New password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              <button type="button" className="btn btn-sm btn-link text-muted p-0" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <div className="mb-3">
            <label className="form-label small text-uppercase fw-semibold text-muted">Confirm Password</label>
            <div className="auth-input-group">
              <Lock size={16} className="input-icon" />
              <input type={showPassword ? 'text' : 'password'} placeholder="Confirm password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
            </div>
          </div>
          {error && <div className="alert alert-danger py-2 small">{error}</div>}
          <button type="submit" className="btn btn-primary w-100 py-2 fw-semibold" disabled={loading}>
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPasswordConfirm;