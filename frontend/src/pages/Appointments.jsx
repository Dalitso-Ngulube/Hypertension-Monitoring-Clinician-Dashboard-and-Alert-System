import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosConfig';
import { Calendar, Clock, User, Plus, X, Edit, CheckCircle, Clock as ClockIcon, AlertCircle } from 'lucide-react';

const Appointments = () => {
  const { user } = useContext(AuthContext);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [patients, setPatients] = useState([]);
  const [formData, setFormData] = useState({ patient: '', date: '', time: '', reason: '' });
  const [error, setError] = useState('');
  
  // State for viewing/editing appointment
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [updating, setUpdating] = useState(false);

  const fetchAppointments = async () => {
    setLoading(true);
    try {
      const response = await api.get('/appointments/appointments/');
      const sorted = (response.data.results || response.data).sort((a, b) => {
        if (a.date < b.date) return -1;
        if (a.date > b.date) return 1;
        return a.time < b.time ? -1 : 1;
      });
      setAppointments(sorted);
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, []);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const response = await api.get('/patients/');
        setPatients(response.data.results || []);
      } catch (error) {
        console.error('Error fetching patients:', error);
      }
    };
    if (showModal) fetchPatients();
  }, [showModal]);

  const handleAddAppointment = async (e) => {
    e.preventDefault();
    try {
      await api.post('/appointments/appointments/', formData);
      setShowModal(false);
      setFormData({ patient: '', date: '', time: '', reason: '' });
      fetchAppointments();
    } catch (error) {
      setError('Failed to create appointment.');
    }
  };

  const handleStatusUpdate = async (status) => {
    if (!selectedAppointment) return;
    setUpdating(true);
    try {
      await api.patch(`/appointments/appointments/${selectedAppointment.id}/`, { status });
      // Refresh list
      await fetchAppointments();
      // Update selected appointment in the modal
      const updated = appointments.find(a => a.id === selectedAppointment.id);
      setSelectedAppointment(updated || selectedAppointment);
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update status.');
    } finally {
      setUpdating(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'SCHEDULED': return <span className="badge bg-primary bg-opacity-10 text-primary">Scheduled</span>;
      case 'COMPLETED': return <span className="badge bg-success bg-opacity-10 text-success">Completed</span>;
      case 'CANCELLED': return <span className="badge bg-danger bg-opacity-10 text-danger">Cancelled</span>;
      default: return <span className="badge bg-secondary bg-opacity-10 text-secondary">{status}</span>;
    }
  };

  const formatTime = (time) => {
    const [h, m] = time.split(':');
    const hour = parseInt(h);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const h12 = hour % 12 || 12;
    return `${h12}:${m} ${ampm}`;
  };

  const openDetailModal = (appointment) => {
    setSelectedAppointment(appointment);
    setShowDetailModal(true);
  };

  if (!user) return null;

  const canManageAppointments = user.role === 'clinician' || user.role === 'admin';

  return (
    <div className="container-fluid py-4">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h1 className="sidebar-page-heading fw-bold">Appointments</h1>
          <p className="text-muted small">Manage all patient appointments</p>
        </div>
        {canManageAppointments && (
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={16} className="me-1" /> Add Appointment
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-5"><div className="spinner-border text-primary" /></div>
      ) : appointments.length === 0 ? (
        <div className="card card-clinical text-center py-5">
          <Calendar size={48} className="mx-auto text-muted mb-3" />
          <h5>No Appointments</h5>
          <p className="text-muted small">Schedule your first appointment using the "Add Appointment" button.</p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead className="table-light">
              <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Patient</th>
                <th>Reason</th>
                <th>Status</th>
                <th className="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map((apt) => (
                <tr key={apt.id}>
                  <td>
                    <span className="fw-semibold">
                      {new Date(apt.date + 'T00:00:00').toLocaleDateString('en-US', {
                        weekday: 'short',
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </span>
                  </td>
                  <td>
                    <span className="fw-semibold">{formatTime(apt.time)}</span>
                  </td>
                  <td>
                    <div className="d-flex align-items-center gap-2">
                      <div className="bg-primary bg-opacity-10 rounded-circle d-flex align-items-center justify-content-center" style={{ width: 28, height: 28 }}>
                        <span className="fw-bold small text-primary">{apt.patient_name?.charAt(0) || '?'}</span>
                      </div>
                      <span>{apt.patient_name}</span>
                    </div>
                  </td>
                  <td>{apt.reason || <span className="text-muted">—</span>}</td>
                  <td>{getStatusBadge(apt.status)}</td>
                  <td className="text-center">
                    <button className="btn btn-sm btn-outline-primary" onClick={() => openDetailModal(apt)}>
                      <Edit size={14} className="me-1" /> View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Appointment Modal */}
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
                <h5 className="modal-title">Add Appointment</h5>
                <button className="btn-close" onClick={() => setShowModal(false)} />
              </div>
              <form onSubmit={handleAddAppointment}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Patient</label>
                    <select
                      className="form-select"
                      value={formData.patient}
                      onChange={(e) => setFormData({ ...formData, patient: e.target.value })}
                      required
                    >
                      <option value="">Select patient</option>
                      {patients.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.first_name} {p.last_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Date</label>
                    <input
                      type="date"
                      className="form-control"
                      value={formData.date}
                      onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Time</label>
                    <input
                      type="time"
                      className="form-control"
                      value={formData.time}
                      onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Reason</label>
                    <textarea
                      className="form-control"
                      value={formData.reason}
                      onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                      rows="2"
                    />
                  </div>
                  {error && <div className="alert alert-danger py-1 small">{error}</div>}
                </div>
                <div className="modal-footer">
                  <button type="submit" className="btn btn-primary">Create Appointment</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* View/Edit Appointment Modal */}
      {showDetailModal && selectedAppointment && (
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
                <h5 className="modal-title">Appointment Details</h5>
                <button className="btn-close" onClick={() => setShowDetailModal(false)} />
              </div>
              <div className="modal-body">
                <div className="mb-3">
                  <label className="fw-semibold text-muted small text-uppercase">Patient</label>
                  <p className="fw-bold">{selectedAppointment.patient_name}</p>
                </div>
                <div className="row mb-3">
                  <div className="col-6">
                    <label className="fw-semibold text-muted small text-uppercase">Date</label>
                    <p>{new Date(selectedAppointment.date + 'T00:00:00').toLocaleDateString('en-US', {
                      weekday: 'long',
                      month: 'long',
                      day: 'numeric',
                      year: 'numeric'
                    })}</p>
                  </div>
                  <div className="col-6">
                    <label className="fw-semibold text-muted small text-uppercase">Time</label>
                    <p>{formatTime(selectedAppointment.time)}</p>
                  </div>
                </div>
                <div className="mb-3">
                  <label className="fw-semibold text-muted small text-uppercase">Reason</label>
                  <p>{selectedAppointment.reason || 'No reason provided'}</p>
                </div>
                <div className="mb-3">
                  <label className="fw-semibold text-muted small text-uppercase">Current Status</label>
                  <div className="mt-1">{getStatusBadge(selectedAppointment.status)}</div>
                </div>
                {canManageAppointments && <div className="mb-3">
                  <label className="fw-semibold text-muted small text-uppercase">Change Status</label>
                  <div className="d-flex gap-2 mt-1">
                    {['SCHEDULED', 'COMPLETED', 'CANCELLED'].map((status) => (
                      <button
                        key={status}
                        className={`btn btn-sm ${selectedAppointment.status === status ? 'btn-primary' : 'btn-outline-secondary'}`}
                        onClick={() => handleStatusUpdate(status)}
                        disabled={updating || selectedAppointment.status === status}
                      >
                        {status.charAt(0) + status.slice(1).toLowerCase()}
                      </button>
                    ))}
                  </div>
                </div>}
                {updating && (
                  <div className="text-center text-muted small">Updating...</div>
                )}
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={() => setShowDetailModal(false)}>Close</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Appointments;