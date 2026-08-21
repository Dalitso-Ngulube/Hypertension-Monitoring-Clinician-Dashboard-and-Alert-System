// src/App.jsx
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import SessionManager from './components/SessionManager';
import AppContent from './AppContent';
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <SessionManager>
          <BrowserRouter>
            <AppContent /> 
          </BrowserRouter>
        </SessionManager>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;