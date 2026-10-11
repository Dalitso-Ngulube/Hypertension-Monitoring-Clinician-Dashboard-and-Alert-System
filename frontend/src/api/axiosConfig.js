import axios from 'axios';

const TOKEN_KEYS = {
  access: 'access',
  refresh: 'refresh',
};

// Use environment variable if set, otherwise use the IPv4 loopback address.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ──────────────────────────────────────────────────────────────
// Request Interceptor – Attach JWT token to every request
// ──────────────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEYS.access);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ──────────────────────────────────────────────────────────────
// Response Interceptor – Handle token expiry & refresh
// ──────────────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response, // Pass through successful responses
  async (error) => {
    const originalRequest = error.config;
    const detail = error.response?.data?.detail;
    const isAuthenticationFailure =
      error.response?.status === 401 ||
      (error.response?.status === 403 && (
        error.response?.data?.code === 'token_not_valid' ||
        detail === 'Authentication credentials were not provided.'
      ));

    // Refresh expired or invalid JWTs once before logging the user out.
    if (isAuthenticationFailure && !originalRequest._retry && !originalRequest.url?.includes('/auth/token/refresh/')) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem(TOKEN_KEYS.refresh);
        if (!refreshToken) {
          logout();
          return Promise.reject(error);
        }

        // Call the refresh endpoint
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const newAccessToken = response.data.access;
        localStorage.setItem(TOKEN_KEYS.access, newAccessToken);

        // Retry the original request with the new token
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed → clear tokens and redirect to login
        logout();
        return Promise.reject(refreshError);
      }
    }

    // Permission 403s are preserved for the page to handle; only authentication
    // failures clear the session above.
    return Promise.reject(error);
  }
);

// ──────────────────────────────────────────────────────────────
// Helper: Clear tokens and redirect to login page
// ──────────────────────────────────────────────────────────────
function logout() {
  localStorage.removeItem(TOKEN_KEYS.access);
  localStorage.removeItem(TOKEN_KEYS.refresh);
  // Redirect to login if not already there
  if (window.location.pathname !== '/') {
    window.location.href = '/';
  }
}

export default api;