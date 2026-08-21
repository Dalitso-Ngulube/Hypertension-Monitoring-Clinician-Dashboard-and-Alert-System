import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axiosConfig';
import { Heart, Mail, ArrowLeft } from 'lucide-react';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await api.post('/auth/password-reset/', { email });
      setSuccess(true);
    } catch (err) {
      setError('Failed to send reset link.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-vh-100 d-flex align-items-center justify-content-center" style={{ background: 'var(--bg-body)' }}>
        <div className="auth-card text-center">
          <div className="text-5xl mb-3">📧</div>
          <h2 className="auth-title">Check Your Inbox</h2>
          <p className="auth-subtitle">We've sent a reset link to <strong>{email}</strong>.</p>
          <Link to="/" className="btn btn-primary mt-3">Back to Login</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center" style={{ background: 'var(--bg-body)' }}>
      <div className="auth-card">
        <div className="auth-logo"><Heart size={28} className="text-white" /></div>
        <h2 className="auth-title">Reset Password</h2>
        <p className="auth-subtitle">Enter your email and we'll send you a reset link.</p>
        <form onSubmit={handleSubmit} className="mt-4">
          <div className="mb-3">
            <label className="form-label small text-uppercase fw-semibold text-muted">Email Address</label>
            <div className="auth-input-group">
              <Mail size={16} className="input-icon" />
              <input type="email" placeholder="your@email.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
          </div>
          {error && <div className="alert alert-danger py-2 small">{error}</div>}
          <button type="submit" className="btn btn-primary w-100 py-2 fw-semibold" disabled={loading}>
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>
        <div className="text-center mt-3">
          <Link to="/" className="small text-muted"><ArrowLeft size={14} className="me-1" /> Back to Login</Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;