import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosConfig';
import { Calendar, Plus, ChevronLeft, ChevronRight } from 'lucide-react';

const AppointmentCalendar = () => {
  const { user } = useContext(AuthContext);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [patients, setPatients] = useState([]);
  const [formData, setFormData] = useState({ patient: '', date: '', time: '', reason: '' });
  const [error, setError] = useState('');
  const [currentDate, setCurrentDate] = useState(new Date());

  const locale = 'en-ZM';
  const timeZone = 'Africa/Lusaka';

  // Fetch appointments for the current month
  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        const start = new Date(year, month, 1);
        const end = new Date(year, month + 1, 0);
        const response = await api.get('/appointments/appointments/', {
          params: {
            date__gte: start.toISOString().split('T')[0],
            date__lte: end.toISOString().split('T')[0],
          },
        });
        setAppointments(response.data.results || response.data);
      } catch (error) {
        console.error('Error fetching appointments:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAppointments();
  }, [currentDate]);

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
      // Refresh appointments
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();
      const start = new Date(year, month, 1);
      const end = new Date(year, month + 1, 0);
      const response = await api.get('/appointments/appointments/', {
        params: {
          date__gte: start.toISOString().split('T')[0],
          date__lte: end.toISOString().split('T')[0],
        },
      });
      setAppointments(response.data.results || response.data);
    } catch (error) {
      setError('Failed to create appointment.');
    }
  };

  const getAppointmentsForDate = (dateStr) => {
    return appointments.filter((a) => a.date === dateStr);
  };

  const formatDate = (date) => date.toISOString().split('T')[0];

  // Build calendar grid
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();

  const monthName = currentDate.toLocaleString(locale, { month: 'long', timeZone });
  const yearName = currentDate.getFullYear();

  const goToPrevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const goToNextMonth = () => setCurrentDate(new Date(year, month + 1, 1));
  const goToToday = () => setCurrentDate(new Date());

  // Build calendar cells (Monday first)
  const startOffset = (firstDay === 0) ? 6 : firstDay - 1;
  const totalCells = Math.ceil((startOffset + daysInMonth) / 7) * 7;
  const cells = [];
  for (let i = startOffset - 1; i >= 0; i--) {
    cells.push({ day: daysInPrevMonth - i, isCurrentMonth: false });
  }
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ day: d, isCurrentMonth: true });
  }
  for (let d = 1; d <= totalCells - cells.length; d++) {
    cells.push({ day: d, isCurrentMonth: false });
  }

  // Group cells into weeks
  const weeks = [];
  for (let i = 0; i < cells.length; i += 7) {
    weeks.push(cells.slice(i, i + 7));
  }

  const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const todayStr = formatDate(new Date());

  // Upcoming appointments (next 7 days)
  const upcomingAppointments = appointments
    .filter(a => a.date >= todayStr)
    .sort((a, b) => a.date.localeCompare(b.date) || a.time.localeCompare(b.time))
    .slice(0, 5);

  const lightGreenBg = { backgroundColor: '#f0faf0' };

  return (
    <div className="card card-clinical shadow-sm border-0">
      {/* Header with light green background */}
      <div className="card-header bg-transparent border-bottom-0 pt-3 d-flex flex-wrap justify-content-between align-items-center" style={lightGreenBg}>
        <h5 className="fw-semibold mb-0">
          <Calendar size={18} className="me-2 text-primary" /> Appointment
        </h5>
        <div className="d-flex align-items-center gap-2">
          <button className="btn btn-sm btn-outline-secondary" onClick={goToPrevMonth}>
            <ChevronLeft size={16} />
          </button>
          <span className="fw-semibold text-dark">
            {monthName} {yearName}
          </span>
          <button className="btn btn-sm btn-outline-secondary" onClick={goToNextMonth}>
            <ChevronRight size={16} />
          </button>
          <button className="btn btn-sm btn-outline-primary" onClick={goToToday}>
            Today
          </button>
          <button className="btn btn-sm btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={14} className="me-1" /> Add
          </button>
        </div>
      </div>

      <div className="card-body pt-2">
        {loading ? (
          <div className="text-center py-3 text-muted">Loading appointments...</div>
        ) : (
          <>
            {/* Calendar Grid */}
            <div className="calendar-grid">
              <div className="row g-0 mb-2">
                {weekdays.map((day) => (
                  <div key={day} className="col text-center small fw-semibold text-muted text-uppercase">
                    {day}
                  </div>
                ))}
              </div>
              {weeks.map((week, weekIndex) => (
                <div key={weekIndex} className="row g-0">
                  {week.map((cell, cellIndex) => {
                    const dateObj = new Date(
                      cell.isCurrentMonth ? year : month === 0 ? year - 1 : year,
                      cell.isCurrentMonth ? month : month === 0 ? 11 : month - 1,
                      cell.day
                    );
                    const dateStr = formatDate(dateObj);
                    const isToday = dateStr === todayStr;
                    const isCurrentMonth = cell.isCurrentMonth;

                    return (
                      <div
                        key={cellIndex}
                        className="col text-center p-1"
                        style={{ opacity: isCurrentMonth ? 1 : 0.3 }}
                      >
                        <div
                          className={`small fw-semibold ${
                            isToday ? 'text-primary' : isCurrentMonth ? 'text-dark' : ''
                          }`}
                          style={{
                            width: '100%',
                            padding: '4px 0',
                            borderRadius: '50%',
                            backgroundColor: isToday ? 'var(--medical-100)' : 'transparent',
                            transition: 'background-color 0.15s ease',
                          }}
                        >
                          {cell.day}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>

            {/* Upcoming Appointments with light green background */}
            <div className="mt-4 pt-3 border-top border-light" style={lightGreenBg}>
              <h6 className="small fw-semibold text-muted">Upcoming Appointments</h6>
              {upcomingAppointments.length === 0 ? (
                <p className="text-muted small">No appointments in the next 7 days.</p>
              ) : (
                <div className="mt-1">
                  {upcomingAppointments.map((apt) => {
                    const aptDate = new Date(apt.date + 'T00:00:00');
                    const dateStr = aptDate.toLocaleDateString(locale, {
                      month: 'short',
                      day: 'numeric',
                      timeZone,
                    });
                    const startTime = apt.time.slice(0, 5);
                    return (
                      <div
                        key={apt.id}
                        className="d-flex align-items-center py-1 border-bottom border-light"
                      >
                        <div className="me-3" style={{ minWidth: '70px' }}>
                          <span className="fw-semibold text-dark small">{dateStr}</span>
                        </div>
                        <div className="me-3">
                          <span className="text-muted small">{startTime}</span>
                        </div>
                        <div className="flex-grow-1">
                          <span className="fw-semibold text-dark small">{apt.patient_name}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}
      </div>

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
    </div>
  );
};

export default AppointmentCalendar;