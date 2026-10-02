import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosConfig';
import RiskPieChart from '../components/RiskPieChart';
import TrendChart from '../components/TrendChart';
import { Users, Activity, AlertTriangle, TrendingUp, Download } from 'lucide-react';

const Analytics = () => {
  const { user } = useContext(AuthContext);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const sumRes = await api.get('/analytics/summary/');
        setSummary(sumRes.data);
        const patRes = await api.get('/patients/');
        setPatients(patRes.data.results || []);
        if (patRes.data.results?.length > 0) setSelectedPatient(patRes.data.results[0].id);
      } catch (error) { console.error(error); } finally { setLoading(false); }
    };
    fetchData();
  }, []);

  if (loading) return <div className="text-center py-5"><div className="spinner-border text-primary" /></div>;

  return (
    <div className="container-fluid py-4">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h1 className="sidebar-page-heading fw-bold">Analytics</h1>
          <p className="text-muted small">Explore detailed patient analytics and trends</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => { const token = localStorage.getItem('access_token'); window.open(`http://localhost:8000/api/analytics/export/summary/?token=${token}`, '_blank'); }}>
          <Download size={16} className="me-1" /> Export Report
        </button>
      </div>

      <div className="row g-3 mb-4">
        {[{ icon: Users, label: 'Total Patients', value: summary?.total_patients || 0, color: 'primary' },
          { icon: Activity, label: 'Readings', value: summary?.total_readings || 0, color: 'success' },
          { icon: AlertTriangle, label: 'Critical Alerts', value: summary?.critical_readings || 0, color: 'danger' },
          { icon: TrendingUp, label: 'Health Score', value: Math.min(100, Math.round((summary?.total_readings || 0) / 50 * 100)) + '%', color: 'info' }
        ].map((stat, idx) => (
          <div key={idx} className="col-6 col-md-3">
            <div className="stat-card">
              <div className={`stat-icon bg-${stat.color} bg-opacity-10 text-${stat.color}`}>
                <stat.icon size={18} />
              </div>
              <div>
                <div className="stat-label">{stat.label}</div>
                <div className="stat-number">{stat.value}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="row g-4">
        <div className="col-lg-6">
          <div className="card card-clinical">
            <div className="card-header">Risk Distribution</div>
            <div className="card-body"><RiskPieChart /></div>
          </div>
        </div>
        <div className="col-lg-6">
          <div className="card card-clinical">
            <div className="card-header">Patient Trend</div>
            <div className="card-body">
              <select className="form-select mb-3" value={selectedPatient || ''} onChange={(e) => setSelectedPatient(parseInt(e.target.value))}>
                {patients.map(p => <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>)}
              </select>
              <TrendChart patientId={selectedPatient} days={30} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;