import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosConfig';
import { AlertTriangle, CheckCircle, Clock, RefreshCw, Filter, Search } from 'lucide-react';

const Alerts = () => {
  const { user } = useContext(AuthContext);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/alerts/unresolved/');
      setAlerts(response.data.results || []);
    } catch (error) { console.error(error); } finally { setLoading(false); }
  };

  useEffect(() => { fetchAlerts(); }, []);

  const handleResolve = async (alertId) => {
    try {
      await api.patch(`/alerts/${alertId}/`, { is_resolved: true });
      setAlerts(alerts.filter(a => a.id !== alertId));
    } catch (error) { console.error(error); }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'bg-danger bg-opacity-10 text-danger';
      case 'HIGH': return 'bg-warning bg-opacity-10 text-warning';
      default: return 'bg-info bg-opacity-10 text-info';
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = alert.patient_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.message?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || alert.severity === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="container-fluid py-4">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h2 fw-bold">Alerts</h1>
          <p className="text-muted small">View and manage all patient alerts</p>
        </div>
        <button className="btn btn-outline-secondary btn-sm" onClick={fetchAlerts}>
          <RefreshCw size={16} className={loading ? 'spinner-border spinner-border-sm me-1' : 'me-1'} /> Refresh
        </button>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <div className="stat-card">
            <div className="stat-icon bg-danger bg-opacity-10 text-danger"><AlertTriangle size={18} /></div>
            <div><div className="stat-label">Critical</div><div className="stat-number">{alerts.filter(a => a.severity === 'CRITICAL').length}</div></div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="stat-card">
            <div className="stat-icon bg-warning bg-opacity-10 text-warning"><AlertTriangle size={18} /></div>
            <div><div className="stat-label">High</div><div className="stat-number">{alerts.filter(a => a.severity === 'HIGH').length}</div></div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="stat-card">
            <div className="stat-icon bg-success bg-opacity-10 text-success"><CheckCircle size={18} /></div>
            <div><div className="stat-label">Resolved</div><div className="stat-number">0</div></div>
          </div>
        </div>
      </div>

      <div className="d-flex flex-wrap gap-3 mb-4">
        <div className="input-group" style={{ maxWidth: '300px' }}>
          <span className="input-group-text bg-white border-end-0"><Search size={16} className="text-muted" /></span>
          <input type="text" className="form-control border-start-0" placeholder="Search alerts..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
        </div>
        <div className="input-group" style={{ maxWidth: '200px' }}>
          <span className="input-group-text bg-white"><Filter size={16} className="text-muted" /></span>
          <select className="form-select" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-5"><div className="spinner-border text-primary" /></div>
      ) : filteredAlerts.length === 0 ? (
        <div className="card card-clinical text-center py-5">
          <CheckCircle size={48} className="mx-auto text-success mb-3" />
          <h5>No Alerts</h5>
          <p className="text-muted small">All patients are stable. No unresolved alerts found.</p>
        </div>
      ) : (
        <div className="row g-3">
          {filteredAlerts.map(alert => (
            <div key={alert.id} className="col-12">
              <div className="card card-clinical border-start border-4 border-danger">
                <div className="card-body d-flex flex-wrap justify-content-between align-items-center gap-2">
                  <div>
                    <div className="d-flex flex-wrap align-items-center gap-2">
                      <span className={`badge ${getSeverityColor(alert.severity)}`}>{alert.severity}</span>
                      <span className="fw-semibold">{alert.patient_name}</span>
                      <span className="small text-muted"><Clock size={12} className="me-1" />{new Date(alert.created_at).toLocaleString()}</span>
                    </div>
                    <p className="mb-0 small text-secondary mt-1">{alert.message}</p>
                  </div>
                  <button className="btn btn-sm btn-outline-success" onClick={() => handleResolve(alert.id)}>
                    <CheckCircle size={14} className="me-1" /> Resolve
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Alerts;