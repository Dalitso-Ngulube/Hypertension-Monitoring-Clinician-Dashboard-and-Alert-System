import React, { useContext } from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider, AuthContext } from '../AuthContext';
import api from '../../api/axiosConfig';
import Login from '../../pages/Login';

jest.mock('../../api/axiosConfig', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

const AuthProbe = () => {
  const { isAuthenticated, user, loading } = useContext(AuthContext);

  return (
    <div>
      <span data-testid="auth-state">{loading ? 'loading' : isAuthenticated ? 'authenticated' : 'unauthenticated'}</span>
      <span data-testid="user-role">{user?.role || 'none'}</span>
    </div>
  );
};

describe('AuthProvider', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('rehydrates the active user from the persisted access token', async () => {
    localStorage.setItem('access', 'stored-access-token');
    api.get.mockResolvedValue({
      data: { username: 'alice', role: 'clinician' },
    });

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-state')).toHaveTextContent('authenticated');
    });

    expect(api.get).toHaveBeenCalledWith('/auth/me/');
    expect(screen.getByTestId('user-role')).toHaveTextContent('clinician');
  });

  it('clears the auth session when the stored token is invalid', async () => {
    localStorage.setItem('access', 'expired-token');
    localStorage.setItem('refresh', 'expired-refresh');
    api.get.mockRejectedValue({ response: { status: 401 } });

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(localStorage.getItem('access')).toBeNull();
      expect(localStorage.getItem('refresh')).toBeNull();
    });

    expect(screen.getByTestId('auth-state')).toHaveTextContent('unauthenticated');
  });

  it('persists tokens returned after login and keeps them under the expected names', async () => {
    const mockLogin = jest.fn().mockResolvedValue({ role: 'admin' });
    api.post.mockResolvedValue({
      data: { access: 'login-access-token', refresh: 'login-refresh-token' },
    });

    render(
      <MemoryRouter>
        <AuthContext.Provider value={{ login: mockLogin }}>
          <Login />
        </AuthContext.Provider>
      </MemoryRouter>
    );

    screen.getByPlaceholderText('Enter your username').value = 'alice';
    screen.getByPlaceholderText('Enter your password').value = 'secret';
    screen.getByRole('button', { name: 'Log in' }).click();

    await waitFor(() => {
      expect(localStorage.getItem('access')).toBe('login-access-token');
      expect(localStorage.getItem('refresh')).toBe('login-refresh-token');
    });

    expect(mockLogin).toHaveBeenCalledTimes(1);
  });
});
