import React, { createContext, useState, useEffect } from 'react';
import api from '../api/axiosConfig';

export const AuthContext = createContext();

const TOKEN_KEYS = {
  access: 'access',
  refresh: 'refresh',
};

const clearStoredTokens = () => {
  localStorage.removeItem(TOKEN_KEYS.access);
  localStorage.removeItem(TOKEN_KEYS.refresh);
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = async () => {
    try {
      const token = localStorage.getItem(TOKEN_KEYS.access);
      console.log(' fetchUser - token present?', !!token);
      if (!token) {
        console.log(' No token, stopping fetch');
        setLoading(false);
        setIsAuthenticated(false);
        setUser(null);
        return;
      }
      console.log(' Fetching user from /auth/me/');
      const response = await api.get('/auth/me/');
      console.log(' User fetched:', response.data);
      setUser(response.data);
      setIsAuthenticated(true);
      return response.data;
    } catch (error) {
      console.error(' Failed to fetch user:', error);
      if (error.response?.status === 403 || error.response?.status === 401) {
        console.warn(' Token invalid/expired, logging out');
        clearStoredTokens();
        setIsAuthenticated(false);
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  // Standard login – waits for the user profile before protected navigation
  const login = async () => {
    console.log(' login() called');
    return fetchUser();
  };

  // Immediate login – sets authenticated first, then fetches user in background
  const immediateLogin = () => {
    console.log(' immediateLogin() called – setting isAuthenticated = true');
    setIsAuthenticated(true);
    fetchUser(); // fetch in background
  };

  const logout = () => {
    console.warn(' logout() called – clearing tokens and state');
    clearStoredTokens();
    setIsAuthenticated(false);
    setUser(null);
    setLoading(false);
  };

  console.log(' AuthProvider state:', { isAuthenticated, user, loading });

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        login,
        logout,
        loading,
        immediateLogin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};