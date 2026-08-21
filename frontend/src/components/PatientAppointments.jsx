import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosConfig';
import { Calendar, Clock, User } from 'lucide-react';

const PatientAppointments = () => {
  const { user } = useContext(AuthContext);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const response = await api.get('/appointments/appointments/');
        setAppointments(response.data.results || response.data);
      } catch (error) {
        console.error('Error fetching appointments:', error);
      } finally {
        setLoading(false);
      }
    };
    if (user) fetchAppointments();
  }, [user]);

  if (loading) return <div className="text-center py-3 text-muted">Loading appointments...</div>;

  if (appointments.length === 0) {
    return <p className="text-muted small">No appointments scheduled.</p>;
  }

  return (
    <div className="mt-2">
      {appointments.slice(0, 5).map((apt) => {
        const date = new Date(apt.date + 'T00:00:00');
        const dateStr = date.toLocaleDateString('en-ZM', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        });
        const timeStr = apt.time.slice(0, 5);
        return (
          <div
            key={apt.id}
            className="d-flex align-items-center py-2 border-bottom border-light"
          >
            <div className="me-3" style={{ minWidth: '80px' }}>
              <span className="fw-semibold text-dark small">{dateStr}</span>
            </div>
            <div className="me-3">
              <span className="text-muted small">{timeStr}</span>
            </div>
            <div className="flex-grow-1">
              <span className="fw-semibold text-dark small">{apt.patient_name}</span>
            </div>
            <span className="badge bg-primary bg-opacity-10 text-primary small">
              {apt.status}
            </span>
          </div>
        );
      })}
      {appointments.length > 5 && (
        <div className="mt-2 text-center">
          <span className="text-muted small">+ {appointments.length - 5} more</span>
        </div>
      )}
    </div>
  );
};

export default PatientAppointments;