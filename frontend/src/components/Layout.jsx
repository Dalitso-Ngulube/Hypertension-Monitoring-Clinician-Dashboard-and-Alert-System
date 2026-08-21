import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import Sidebar from './Sidebar';
import PatientSidebar from './PatientSidebar';

const Layout = ({ children }) => {
  const { user } = useContext(AuthContext);
  const [collapsed, setCollapsed] = useState(false);
  const toggleSidebar = () => setCollapsed(!collapsed);

  const isPatient = user?.role === 'patient';
  const SidebarComponent = isPatient ? PatientSidebar : Sidebar;

  return (
    <div className="d-flex min-vh-100">
      <SidebarComponent collapsed={collapsed} toggleSidebar={toggleSidebar} />
      <main
        className={`flex-grow-1 p-4 transition-all ${
          collapsed ? 'ms-0' : 'ms-230'
        }`}
        style={{ backgroundColor: 'var(--bg-body)' }}
      >
        {children}
      </main>
    </div>
  );
};

export default Layout;