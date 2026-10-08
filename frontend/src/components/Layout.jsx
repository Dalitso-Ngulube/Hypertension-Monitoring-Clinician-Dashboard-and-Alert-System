import React, { useState, useContext, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import Sidebar from './Sidebar';
import PatientSidebar from './PatientSidebar';

const Layout = ({ children }) => {
  const { user } = useContext(AuthContext);
  const [collapsed, setCollapsed] = useState(() => window.innerWidth < 768);
  const toggleSidebar = () => setCollapsed(!collapsed);

  useEffect(() => {
    const handleResize = () => {
      setCollapsed(window.innerWidth < 768);
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isPatient = user?.role === 'patient';
  const SidebarComponent = isPatient ? PatientSidebar : Sidebar;

  return (
    <div className="d-flex min-vh-100 layout-shell">
      <SidebarComponent collapsed={collapsed} toggleSidebar={toggleSidebar} />
      <main
        className={`flex-grow-1 transition-all main-content ${
          collapsed ? 'sidebar-collapsed' : 'sidebar-open'
        }`}
        style={{ backgroundColor: 'var(--bg-body)' }}
      >
        {children}
      </main>
    </div>
  );
};

export default Layout;