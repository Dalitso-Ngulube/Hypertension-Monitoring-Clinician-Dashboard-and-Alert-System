import React, { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import { Calendar, Clock, Activity, Droplet, Heart, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const BPHistoryTable = ({ patientId }) => {
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [averages, setAverages] = useState({ systolic: 0, diastolic: 0, pulse: 0, count: 0 });

  useEffect(() => {
    const fetchReadings = async () => {
      setLoading(true);
      try {
        // If patientId is provided, fetch for that patient, else fetch for the logged-in user
        const url = patientId ? `/bp_readings/?patient=${patientId}` : '/bp_readings/';
        const response = await api.get(url);
        const data = response.data.results || [];

        // Sort: newest first
        const sorted = data.sort((a, b) => new Date(b.recorded_at) - new Date(a.recorded_at));
        setReadings(sorted);

        if (sorted.length > 0) {
          const totalSystolic = sorted.reduce((sum, r) => sum + r.systolic, 0);
          const totalDiastolic = sorted.reduce((sum, r) => sum + r.diastolic, 0);
          const totalPulse = sorted.reduce((sum, r) => sum + (r.pulse_rate || 0), 0);
          const pulseCount = sorted.filter(r => r.pulse_rate).length;

          setAverages({
            systolic: Math.round(totalSystolic / sorted.length),
            diastolic: Math.round(totalDiastolic / sorted.length),
            pulse: pulseCount > 0 ? Math.round(totalPulse / pulseCount) : 0,
            count: sorted.length,
          });
        } else {
          setAverages({ systolic: 0, diastolic: 0, pulse: 0, count: 0 });
        }
      } catch (error) {
        console.error('Error fetching BP history:', error);
        setReadings([]);
        setAverages({ systolic: 0, diastolic: 0, pulse: 0, count: 0 });
      } finally {
        setLoading(false);
      }
    };

    fetchReadings();
  }, [patientId]);

  const getRiskBadge = (category) => {
    const colors = {
      CRISIS: 'bg-danger',
      STAGE_2: 'bg-warning',
      STAGE_1: 'bg-info',
      ELEVATED: 'bg-primary',
      NORMAL: 'bg-success',
    };
    return colors[category] || 'bg-secondary';
  };

  const getTrendIcon = (value, type) => {
    if (readings.length < 2) return <Minus size={14} className="text-muted" />;
    const latest = readings[0][type];
    const previous = readings[1][type];
    if (latest > previous) return <TrendingUp size={14} className="text-danger" />;
    if (latest < previous) return <TrendingDown size={14} className="text-success" />;
    return <Minus size={14} className="text-muted" />;
  };

  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="spinner-border spinner-border-sm text-primary" role="status" />
        <p className="text-muted mt-2">Loading BP history...</p>
      </div>
    );
  }

  if (readings.length === 0) {
    return (
      <div className="card card-clinical text-center py-5">
        <Activity size={40} className="mx-auto text-muted mb-2" />
        <h5 className="text-muted">No BP readings recorded</h5>
        <p className="text-muted small">Add a reading to start tracking.</p>
      </div>
    );
  }

  return (
    <div className="card card-clinical mt-3">
      <div className="card-header d-flex justify-content-between align-items-center">
        <span><Activity size={16} className="me-2" /> BP History</span>
        <span className="badge bg-secondary">{averages.count} readings</span>
      </div>
      <div className="card-body">
        {/* Averages Summary */}
        <div className="row g-3 mb-3">
          <div className="col-6 col-md-4">
            <div className="border rounded p-2 text-center">
              <small className="text-muted d-block">Avg Systolic</small>
              <strong>{averages.systolic} <span className="text-muted small">mmHg</span></strong>
            </div>
          </div>
          <div className="col-6 col-md-4">
            <div className="border rounded p-2 text-center">
              <small className="text-muted d-block">Avg Diastolic</small>
              <strong>{averages.diastolic} <span className="text-muted small">mmHg</span></strong>
            </div>
          </div>
          <div className="col-6 col-md-4">
            <div className="border rounded p-2 text-center">
              <small className="text-muted d-block">Avg Pulse</small>
              <strong>{averages.pulse} <span className="text-muted small">bpm</span></strong>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="table-responsive">
          <table className="table table-hover table-sm">
            <thead className="table-light">
              <tr>
                <th>Date / Time</th>
                <th>Systolic</th>
                <th>Diastolic</th>
                <th>Pulse</th>
                <th>Risk</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {readings.map((reading) => (
                <tr key={reading.id}>
                  <td className="text-nowrap">
                    <Calendar size={12} className="text-muted me-1" />
                    {new Date(reading.recorded_at).toLocaleDateString()}
                    <Clock size={12} className="text-muted ms-2 me-1" />
                    {new Date(reading.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td>
                    {reading.systolic}
                    {readings.length > 1 && reading.id === readings[0].id && (
                      <span className="ms-1">{getTrendIcon(reading, 'systolic')}</span>
                    )}
                  </td>
                  <td>
                    {reading.diastolic}
                    {readings.length > 1 && reading.id === readings[0].id && (
                      <span className="ms-1">{getTrendIcon(reading, 'diastolic')}</span>
                    )}
                  </td>
                  <td>{reading.pulse_rate || '—'}</td>
                  <td>
                    <span className={`badge ${getRiskBadge(reading.risk_category)}`}>
                      {reading.risk_category || 'UNKNOWN'}
                    </span>
                  </td>
                  <td>{reading.source || 'MANUAL'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default BPHistoryTable;