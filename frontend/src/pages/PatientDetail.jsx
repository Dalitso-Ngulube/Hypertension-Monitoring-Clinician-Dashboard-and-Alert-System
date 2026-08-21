import React, { useState, useEffect, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosConfig';
import MedicalHistory from '../components/MedicalHistory';
import TimeOfDayPatterns from '../components/TimeOfDayPatterns';
import ClinicalDecisionSupport from '../components/ClinicalDecisionSupport';
import RiskAssessment from '../components/RiskAssessment';
import AddReadingModal from '../components/AddReadingModal';
import { User, Mail, Phone, Calendar, MapPin, Download } from 'lucide-react';

const PatientDetail = () => {
  const { id } = useParams();
  const { user } = useContext(AuthContext);
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchPatient = async () => {
    try {
      const response = await api.get(`/patients/${id}/`);
      setPatient(response.data);
    } catch (error) { console.error(error); } finally { setLoading(false); }
  };

  useEffect(() => {
    fetchPatient();
  }, [id, refreshKey]);

  const handleRefresh = () => setRefreshKey(prev => prev + 1);

  const handleExportCSV = () => {
    const token = localStorage.getItem('access_token');
    window.open(`http://localhost:8000/api/analytics/export/patient/${id}/?token=${token}`, '_blank');
  };

  if (loading) return <div className="text-center py-5"><div className="spinner-border text-primary" /></div>;
  if (!patient) return <div className="text-center py-5 text-muted">Patient not found.</div>;

  return (
    <div className="container-fluid py-4">
      <div className="d-flex flex-wrap justify-content-between align-items-start mb-4">
        <div className="card card-clinical flex-grow-1 me-2">
          <div className="card-body d-flex flex-wrap align-items-center gap-4">
            <div className="bg-primary bg-opacity-10 rounded-circle d-flex align-items-center justify-content-center" style={{ width: 64, height: 64 }}>
              <span className="fw-bold fs-2 text-primary">{patient.first_name?.[0]}{patient.last_name?.[0]}</span>
            </div>
            <div className="flex-grow-1">
              <h3 className="fw-bold mb-0">{patient.first_name} {patient.last_name}</h3>
              <p className="text-muted small">Patient ID: {String(patient.id).padStart(4, '0')}</p>
              <div className="d-flex flex-wrap gap-3 small text-secondary">
                <span><Calendar size={14} className="me-1" /> Age: {patient.age}</span>
                <span><User size={14} className="me-1" /> {patient.gender || 'Not specified'}</span>
                <span><Phone size={14} className="me-1" /> {patient.phone_number || 'No phone'}</span>
                <span><Mail size={14} className="me-1" /> {patient.user?.email || 'No email'}</span>
                <span><MapPin size={14} className="me-1" /> {patient.address || 'No address'}</span>
              </div>
            </div>
          </div>
        </div>
        <div className="d-flex gap-2">
          <AddReadingModal patientId={patient.id} patientName={`${patient.first_name} ${patient.last_name}`} onReadingAdded={handleRefresh} />
          <button className="btn btn-primary btn-sm" onClick={handleExportCSV}>
            <Download size={16} className="me-1" /> Export CSV
          </button>
        </div>
      </div>

      <MedicalHistory patientId={patient.id} onUpdate={handleRefresh} />

      <div className="row g-4 mt-2">
        <div className="col-lg-6"><TimeOfDayPatterns patientId={patient.id} /></div>
        <div className="col-lg-6"><RiskAssessment patientId={patient.id} /></div>
      </div>

      <div className="mt-4"><ClinicalDecisionSupport patientId={patient.id} /></div>
    </div>
  );
};

export default PatientDetail;