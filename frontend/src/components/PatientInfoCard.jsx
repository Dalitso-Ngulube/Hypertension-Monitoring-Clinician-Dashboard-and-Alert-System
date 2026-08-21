import React from 'react';
import { HeartPulse, Activity, Droplet, Thermometer } from 'lucide-react';

const PatientInfoCard = ({ patient, latestReading }) => {
  if (!patient) {
    return <div className="profile-card text-center text-muted py-3">Select a patient to view their profile</div>;
  }

  if (!latestReading) {
    return (
      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar" style={{ background: '#2563eb' }}>
            {patient.first_name?.[0]}{patient.last_name?.[0]}
          </div>
          <div>
            <div className="profile-name">{patient.first_name} {patient.last_name}</div>
            <div className="profile-id">ID: {String(patient.id).padStart(4, '0')} • Age: {patient.age}</div>
          </div>
        </div>
        <p className="text-muted text-center">No readings available for this patient.</p>
      </div>
    );
  }

  const getRiskTag = (category) => {
    const map = {
      CRISIS: 'crisis',
      STAGE_2: 'stage-2',
      STAGE_1: 'stage-1',
      ELEVATED: 'elevated',
      NORMAL: 'normal'
    };
    return map[category] || 'normal';
  };

  // Get initials for avatar
  const initials = `${patient.first_name?.[0] || ''}${patient.last_name?.[0] || ''}`.toUpperCase();

  return (
    <div className="profile-card">
      <div className="profile-header">
        <div className="profile-avatar" style={{ background: '#2563eb' }}>
          {initials}
        </div>
        <div className="flex-1">
          <div className="profile-name">{patient.first_name} {patient.last_name}</div>
          <div className="profile-id">ID: {String(patient.id).padStart(4, '0')} • Age: {patient.age}</div>
        </div>
        <span className={`risk-tag ${getRiskTag(latestReading.risk_category)}`}>
          {latestReading.risk_category || 'NORMAL'}
        </span>
      </div>

      <div className="vitals-grid">
        <div className="vital-item">
          <div className="vital-icon"><HeartPulse size={16} /></div>
          <div className="vital-value">{latestReading.systolic}/{latestReading.diastolic}</div>
          <div className="vital-label">BP (mmHg)</div>
        </div>
        <div className="vital-item">
          <div className="vital-icon"><Activity size={16} /></div>
          <div className="vital-value">{latestReading.pulse_rate || '--'}</div>
          <div className="vital-label">Pulse (bpm)</div>
        </div>
        <div className="vital-item">
          <div className="vital-icon"><Droplet size={16} /></div>
          <div className="vital-value">98%</div>
          <div className="vital-label">SpO₂</div>
        </div>
        <div className="vital-item">
          <div className="vital-icon"><Thermometer size={16} /></div>
          <div className="vital-value" style={{
            color: latestReading.risk_category === 'CRISIS' ? '#b91c1c' : '#0b8a5e'
          }}>
            {latestReading.risk_category === 'CRISIS' ? 'Critical' : 'Stable'}
          </div>
          <div className="vital-label">Status</div>
        </div>
      </div>
    </div>
  );
};

export default PatientInfoCard;