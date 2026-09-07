import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosConfig';
import { HeartPulse, Activity, Droplet, Thermometer, Plus, X } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import BPHistoryTable from '../components/BPHistoryTable';   // <-- ADDED

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const PatientDashboard = () => {
  const { user, logout } = useContext(AuthContext);
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ systolic: '', diastolic: '', pulse_rate: '' });
  const [error, setError] = useState('');
  const [summary, setSummary] = useState(null);

  const fetchData = async () => {
    try {
      const readingsRes = await api.get('/bp_readings/');
      setReadings(readingsRes.data.results || []);
      const summaryRes = await api.get('/analytics/summary/');
      setSummary(summaryRes.data);
    } catch (error) {
      console.error('Error fetching patient data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddReading = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/bp_readings/patient/add/', formData);
      setShowModal(false);
      setFormData({ systolic: '', diastolic: '', pulse_rate: '' });
      fetchData();
    } catch (error) {
      setError('Failed to add reading. Please check your values.');
    }
  };

  const sortedReadings = [...readings].sort((a, b) => new Date(a.recorded_at) - new Date(b.recorded_at));
  const labels = sortedReadings.map(r => new Date(r.recorded_at).toLocaleDateString());
  const systolicData = sortedReadings.map(r => r.systolic);
  const diastolicData = sortedReadings.map(r => r.diastolic);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Systolic',
        data: systolicData,
        borderColor: '#e53e3e',
        backgroundColor: 'rgba(229,62,62,0.1)',
        tension: 0.2,
        fill: true,
      },
      {
        label: 'Diastolic',
        data: diastolicData,
        borderColor: '#3182ce',
        backgroundColor: 'rgba(49,130,206,0.1)',
        tension: 0.2,
        fill: true,
      },
    ],
  };

  if (!user || user.role !== 'patient') {
    return <div className="text-center mt-5">Access denied. Only patients can view this dashboard.</div>;
  }

  const latestReading = readings.length > 0 ? readings[0] : null;

  return (
    <div className="container-fluid py-4" style={{ minHeight: '100vh', backgroundColor: 'var(--bg-body)' }}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h2 fw-bold">My Health Dashboard</h1>
          <p className="text-muted small">Welcome back, {user.username}</p>
        </div>
        <button className="btn btn-outline-danger" onClick={logout}>
          Logout
        </button>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-6 col-md-3">
          <div className="stat-card">
            <div className="stat-icon bg-primary bg-opacity-10 text-primary">
              <HeartPulse size={18} />
            </div>
            <div>
              <div className="stat-label">Latest BP</div>
              <div className="stat-number">{latestReading ? `${latestReading.systolic}/${latestReading.diastolic}` : '--'}</div>
            </div>
          </div>
        </div>
        <div className="col-6 col-md-3">
          <div className="stat-card">
            <div className="stat-icon bg-success bg-opacity-10 text-success">
              <Activity size={18} />
            </div>
            <div>
              <div className="stat-label">Total Readings</div>
              <div className="stat-number">{summary?.total_readings || 0}</div>
            </div>
          </div>
        </div>
        <div className="col-6 col-md-3">
          <div className="stat-card">
            <div className="stat-icon bg-warning bg-opacity-10 text-warning">
              <Droplet size={18} />
            </div>
            <div>
              <div className="stat-label">Avg Systolic</div>
              <div className="stat-number">
                {readings.length ? Math.round(readings.reduce((s, r) => s + r.systolic, 0) / readings.length) : '--'}
              </div>
            </div>
          </div>
        </div>
        <div className="col-6 col-md-3">
          <div className="stat-card">
            <div className="stat-icon bg-info bg-opacity-10 text-info">
              <Thermometer size={18} />
            </div>
            <div>
              <div className="stat-label">Avg Diastolic</div>
              <div className="stat-number">
                {readings.length ? Math.round(readings.reduce((s, r) => s + r.diastolic, 0) / readings.length) : '--'}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card card-clinical mb-4">
        <div className="card-header">Blood Pressure Trend</div>
        <div className="card-body">
          {readings.length > 0 ? (
            <Line data={chartData} options={{ responsive: true, plugins: { legend: { position: 'top' } } }} />
          ) : (
            <p className="text-center text-muted py-4">No readings yet. Add your first reading!</p>
          )}
        </div>
      </div>

      {/* BP History Table added here */}
      <BPHistoryTable />

      <button
        className="btn btn-primary rounded-circle p-3 shadow-lg position-fixed"
        style={{ bottom: '2rem', right: '2rem', zIndex: 1050 }}
        onClick={() => setShowModal(true)}
      >
        <Plus size={24} />
      </button>

      {showModal && (
        <div
          className="modal show d-block"
          style={{
            backgroundColor: 'rgba(0,0,0,0.5)',
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 1050,
          }}
        >
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Add Blood Pressure Reading</h5>
                <button className="btn-close" onClick={() => setShowModal(false)} />
              </div>
              <form onSubmit={handleAddReading}>
                <div className="modal-body">
                  {error && <div className="alert alert-danger py-1 small">{error}</div>}
                  <div className="mb-3">
                    <label className="form-label">Systolic (mmHg)</label>
                    <input
                      type="number"
                      className="form-control"
                      placeholder="e.g., 120"
                      value={formData.systolic}
                      onChange={(e) => setFormData({ ...formData, systolic: e.target.value })}
                      required
                      min="50"
                      max="250"
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Diastolic (mmHg)</label>
                    <input
                      type="number"
                      className="form-control"
                      placeholder="e.g., 80"
                      value={formData.diastolic}
                      onChange={(e) => setFormData({ ...formData, diastolic: e.target.value })}
                      required
                      min="30"
                      max="200"
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Pulse Rate (optional)</label>
                    <input
                      type="number"
                      className="form-control"
                      placeholder="e.g., 72"
                      value={formData.pulse_rate}
                      onChange={(e) => setFormData({ ...formData, pulse_rate: e.target.value })}
                      min="30"
                      max="220"
                    />
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Add Reading
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientDashboard;