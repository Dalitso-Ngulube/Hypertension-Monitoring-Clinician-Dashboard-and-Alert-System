import React, { useContext, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import PatientDetails from './pages/PatientDetails';
import Alerts from './pages/Alerts';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import Appointments from './pages/Appointments';
import ForgotPassword from './pages/ForgotPassword';
import ResetPasswordConfirm from './pages/ResetPasswordConfirm';
import PatientDashboard from './pages/PatientDashboard';

const PrivateRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, user, loading } = useContext(AuthContext);

  if (loading) {
    return <div className="d-flex min-vh-100 align-items-center justify-content-center"><div className="spinner-border text-primary" role="status" aria-label="Loading session" /></div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/" />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    if (user?.role === 'patient') {
      return <Navigate to="/patient/dashboard" />;
    }
    return <Navigate to="/" />;
  }

  return children;
};

const AppContent = () => {
  const { isAuthenticated, user } = useContext(AuthContext);

  useEffect(() => {
    console.log(' Auth state changed:', { isAuthenticated, user });
  }, [isAuthenticated, user]);

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Login />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password/:uidb64/:token" element={<ResetPasswordConfirm />} />

      {/* Clinician routes */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute allowedRoles={['clinician', 'admin']}>
            <Layout>
              <Dashboard />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/patients"
        element={
          <PrivateRoute allowedRoles={['clinician', 'admin']}>
            <Layout>
              <Patients />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/patients/:id"
        element={
          <PrivateRoute allowedRoles={['clinician', 'admin']}>
            <Layout>
              <PatientDetails />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/alerts"
        element={
          <PrivateRoute allowedRoles={['clinician', 'admin']}>
            <Layout>
              <Alerts />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/analytics"
        element={
          <PrivateRoute allowedRoles={['clinician', 'admin']}>
            <Layout>
              <Analytics />
            </Layout>
          </PrivateRoute>
        }
      />

      {/* Shared routes – accessible by both clinicians and patients */}
      <Route
        path="/appointments"
        element={
          <PrivateRoute allowedRoles={['clinician', 'admin', 'patient']}>
            <Layout>
              <Appointments />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <PrivateRoute allowedRoles={['clinician', 'admin', 'patient']}>
            <Layout>
              <Settings />
            </Layout>
          </PrivateRoute>
        }
      />

      {/* Patient-only route */}
      <Route
        path="/patient/dashboard"
        element={
          <PrivateRoute allowedRoles={['patient']}>
            <Layout>
              <PatientDashboard />
            </Layout>
          </PrivateRoute>
        }
      />
    </Routes>
  );
};

export default AppContent;