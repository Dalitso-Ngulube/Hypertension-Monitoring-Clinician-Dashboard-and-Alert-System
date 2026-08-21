import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useIdleTimeout } from '../hooks/useIdleTimeout';

const SESSION_TIMEOUT = 15 * 60 * 1000; // 15 minutes

const SessionManager = ({ children }) => {
  const { isAuthenticated, logout } = useContext(AuthContext);

  useIdleTimeout(SESSION_TIMEOUT, () => {
    if (isAuthenticated) {
      console.log('User idle for 15 minutes, logging out...');
      logout();
      window.location.href = '/';
    }
  });

  return children;
};

export default SessionManager;