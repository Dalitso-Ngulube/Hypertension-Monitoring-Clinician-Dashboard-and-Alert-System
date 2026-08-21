import React, { useState, useEffect, useContext } from 'react';
import api from '../api/axiosConfig';
import { AuthContext } from '../context/AuthContext';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';

const AlertsList = () => {
  const { user } = useContext(AuthContext);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    try {
      const response = await api.get('/alerts/unresolved/');
      setAlerts(response.data.results || []);
    } catch (error) { console.error(error); } finally { setLoading(false); }
  };

  useEffect(() => { fetchAlerts(); }, []);

  const handleResolve = async (alertId) => {
    try { await api.patch(`/alerts/${alertId}/`, { is_resolved: true }); setAlerts(alerts.filter(a => a.id !== alertId)); } catch (error) { console.error(error); }
  };

  const getBadgeColor = (severity) => {
    if (severity === 'CRITICAL') return 'bg-danger bg-opacity-10 text-danger';
    if (severity === 'HIGH') return 'bg-warning bg-opacity-10 text-warning';
    return 'bg-info bg-opacity-10 text-info';
  };

  const isClinicianOrAdmin = user && (user.role === 'clinician' || user.role === 'admin');

  if (loading) return <div className="text-muted small">Loading alerts...</div>;
  if (alerts.length === 0) return <div className="text-center text-success py-2"><CheckCircle size={16} className="me-1" /> No unresolved alerts</div>;

  return (
    <div>
      {alerts.map(alert => (
        <div key={alert.id} className="alert-item-clinical" style={{ borderLeftColor: alert.severity === 'CRITICAL' ? 'var(--risk-crisis)' : alert.severity === 'HIGH' ? 'var(--risk-stage2)' : 'var(--risk-stage1)' }}>
          <div className="flex-1">
            <div className="d-flex align-items-center gap-2">
              <AlertCircle size={14} className={alert.severity === 'CRITICAL' ? 'text-danger' : 'text-warning'} />
              <span className="fw-semibold small">{alert.patient_name}</span>
              <span className={`badge ${getBadgeColor(alert.severity)}`}>{alert.severity}</span>
            </div>
            <div className="small text-muted">{alert.message}</div>
            <div className="small text-muted"><Clock size={10} className="me-1" />{new Date(alert.created_at).toLocaleString()}</div>
          </div>
          {isClinicianOrAdmin && <button className="btn btn-sm btn-outline-success" onClick={() => handleResolve(alert.id)}>Resolve</button>}
        </div>
      ))}
      {isClinicianOrAdmin && <button className="btn btn-sm btn-outline-secondary mt-2 w-100" onClick={fetchAlerts}>Refresh</button>}
    </div>
  );
};

export default AlertsList;