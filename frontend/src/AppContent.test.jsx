import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import AppContent from './AppContent';
import { AuthContext } from './context/AuthContext';

jest.mock('./api/axiosConfig', () => ({
  __esModule: true,
  default: { get: jest.fn() },
}));
jest.mock('./components/Layout', () => ({ children }) => <>{children}</>);
jest.mock('./pages/Login', () => () => <div>Login page</div>);
jest.mock('./pages/Dashboard', () => () => <div>Dashboard page</div>);
jest.mock('./pages/Patients', () => () => <div>Patients page</div>);
jest.mock('./pages/PatientDetails', () => () => <div>Patient details page</div>);
jest.mock('./pages/Alerts', () => () => <div>Alerts page</div>);
jest.mock('./pages/Analytics', () => () => <div>Analytics page</div>);
jest.mock('./pages/Settings', () => () => <div>Settings page</div>);
jest.mock('./pages/Appointments', () => () => <div>Appointments page</div>);
jest.mock('./pages/ForgotPassword', () => () => <div>Forgot password page</div>);
jest.mock('./pages/ResetPasswordConfirm', () => () => <div>Reset password page</div>);
jest.mock('./pages/PatientDashboard', () => () => <div>Patient dashboard page</div>);

const renderAt = (path) => render(
  <AuthContext.Provider value={{ isAuthenticated: true, user: { role: 'clinician' } }}>
    <MemoryRouter initialEntries={[path]}>
      <AppContent />
    </MemoryRouter>
  </AuthContext.Provider>
);

test('removed risk-assessment route is not reachable', () => {
  renderAt('/risk-assessment/1');
  expect(screen.queryByText(/WHO\/ISH Cardiovascular Risk/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/risk assessment/i)).not.toBeInTheDocument();
});
