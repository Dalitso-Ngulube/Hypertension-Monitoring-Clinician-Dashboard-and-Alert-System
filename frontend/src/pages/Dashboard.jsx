import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import PatientSelector from '../components/PatientSelector';
import PatientInfoCard from '../components/PatientInfoCard';
import TrendChart from '../components/TrendChart';
import RiskPieChart from '../components/RiskPieChart';
import AlertsList from '../components/AlertsList';
import AddPatientModal from '../components/AddPatientModal';
import AppointmentCalendar from '../components/AppointmentCalendar';
import api from '../api/axiosConfig';
import { Users, Activity, AlertTriangle, HeartPulse, Calendar, Heart, TrendingUp, ArrowRight } from 'lucide-react';

const Dashboard = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientDetails, setPatientDetails] = useState(null);
  const [patientReadings, setPatientReadings] = useState([]);
  const [latestReading, setLatestReading] = useState(null);
  const [patients, setPatients] = useState([]);
  const [days, setDays] = useState(30);

  // Fetch patient list once
  useEffect(() => {
    const fetchPatients = async () => {
      if (!user || (user.role !== 'clinician' && user.role !== 'admin')) return;
      try {
        const patRes = await api.get('/patients/');
        const list = patRes.data.results || [];
        setPatients(list);
        if (list.length > 0) {
          setSelectedPatient(list[0].id);
        }
      } catch (err) {
        console.error('Error fetching patient list:', err);
      }
    };
    fetchPatients();
  }, [user]);

  // Fetch patient data whenever selectedPatient changes
  useEffect(() => {
  const fetchPatientData = async () => {
    if (!selectedPatient) return;
    try {
      console.log(' Fetching data for patient:', selectedPatient);
      const [detailsRes, readingsRes] = await Promise.all([
        api.get(`/patients/${selectedPatient}/`),
        api.get(`/bp_readings/?patient=${selectedPatient}`)
      ]);
      console.log(' Patient details:', detailsRes.data);
      console.log(' Readings response:', readingsRes.data);
      
      setPatientDetails(detailsRes.data);
      const readings = readingsRes.data.results || [];
      console.log(' Readings array:', readings);
      setPatientReadings(readings);
      setLatestReading(readings.length > 0 ? readings[0] : null);
      console.log(' Latest reading set:', readings[0] || null);
    } catch (err) {
      console.error(' Error fetching patient data:', err);
    }
  };
  fetchPatientData();
}, [selectedPatient]);
  // Compute stats from selected patient's readings
  const totalReadings = patientReadings.length;
  const totalPatients = patients.length;
  const crisisReadings = patientReadings.filter(r => r.risk_category === 'CRISIS').length;
  const highAlerts = patientReadings.filter(r => r.risk_category === 'STAGE_2' || r.risk_category === 'CRISIS').length;

  const getHealthScore = () => {
    if (totalReadings === 0) return 78;
    const avgSystolic = patientReadings.reduce((sum, r) => sum + r.systolic, 0) / totalReadings;
    const avgDiastolic = patientReadings.reduce((sum, r) => sum + r.diastolic, 0) / totalReadings;
    let score = 100;
    if (avgSystolic > 180 || avgDiastolic > 120) score = 30;
    else if (avgSystolic > 140 || avgDiastolic > 90) score = 50;
    else if (avgSystolic > 130 || avgDiastolic > 80) score = 70;
    else score = 90;
    return Math.max(40, Math.min(100, score));
  };

  if (!user) {
    return <div className="d-flex justify-content-center mt-5"><div className="spinner-border text-primary" /></div>;
  }

  return (
    <div className="container-fluid py-4 dashboard-bg">
      <div className="row align-items-center mb-4">
        <div className="col-md-8">
          <h1 className="display-6 fw-bold">Hi, {user?.username}</h1>
          <p className="text-muted small">Here's your clinical overview for today</p>
        </div>
        <div className="col-md-4 text-md-end">
          <span className="bg-white border rounded-3 px-3 py-2 d-inline-flex align-items-center shadow-sm">
            <Calendar size={16} className="text-secondary me-2" />
            <span className="text-secondary small">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
            </span>
          </span>
        </div>
      </div>

      <div className="row g-3 mb-4">
        {[
          { icon: Users, label: 'Patients', value: totalPatients ? totalPatients : 0, color: 'primary' },
          { icon: Activity, label: 'Readings', value: totalReadings, color: 'success' },
          { icon: AlertTriangle, label: 'High Alerts', value: highAlerts, color: 'warning' },
          { icon: HeartPulse, label: 'Crisis', value: crisisReadings, color: 'danger' },
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
        <div className="col-lg-8">
          <div className="card card-clinical mb-3">
            <div className="card-body d-flex flex-wrap justify-content-between align-items-center gap-2">
              <div className="flex-grow-1" style={{ minWidth: '200px' }}>
                <PatientSelector onSelectPatient={setSelectedPatient} />
              </div>
              {user.role !== 'patient' && (
                <AddPatientModal
                  onPatientAdded={(newPatient) => {
                    navigate(`/patients/${newPatient.id}`);
                  }}
                />
              )}
            </div>
          </div>

          {/* PatientInfoCard with a key that changes with the patient */}
          <PatientInfoCard
            key={`${selectedPatient}-${latestReading?.id || ''}`}
            patient={patientDetails}
            latestReading={latestReading}
          />

          <div className="card card-clinical mt-3">
            <div className="card-header d-flex flex-wrap justify-content-between align-items-center">
              <span><TrendingUp size={16} className="me-1" /> Blood Pressure Trends</span>
              <div className="btn-group btn-group-sm">
                {[7, 30, 90].map(d => (
                  <button
                    key={d}
                    className={`btn btn-outline-primary ${days === d ? 'active' : ''}`}
                    onClick={() => setDays(d)}
                  >
                    {d}D
                  </button>
                ))}
              </div>
            </div>
            <div className="card-body">
              <TrendChart patientId={selectedPatient} days={days} />
            </div>
          </div>
        </div>

        <div className="col-lg-4">
          <div className="card card-clinical text-center p-4 mb-3">
            <div
              className="health-score-ring mx-auto"
              style={{
                background: `conic-gradient(#2563eb 0% ${getHealthScore()}%, #e2e8f0 ${getHealthScore()}% 100%)`,
              }}
            >
              <div className="bg-white rounded-circle w-100 h-100 d-flex align-items-center justify-content-center">
                <span className="fw-bold fs-2">{getHealthScore()}%</span>
              </div>
            </div>
            <h5 className="fw-bold mt-2">Overall Health Status</h5>
            <p className="text-muted small">{totalReadings} readings • {crisisReadings} crisis events</p>
          </div>

          <div className="card card-clinical mb-3">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6 className="fw-semibold mb-1">Heart Function</h6>
                  <p className="h3 fw-bold mb-1">{getHealthScore()}%</p>
                  <span className="badge bg-warning text-dark">Moderate</span>
                </div>
                <div className="bg-primary bg-opacity-10 rounded-circle p-3">
                  <Heart size={28} className="text-primary" />
                </div>
              </div>
              <div className="mt-3 pt-2 border-top">
                <div className="d-flex justify-content-between small">
                  <span className="text-muted">Oxygen Saturation</span>
                  <span className="fw-semibold text-success">96%</span>
                </div>
                <div className="progress mt-1" style={{ height: '6px' }}>
                  <div className="progress-bar bg-success" style={{ width: '96%' }} />
                </div>
              </div>
            </div>
          </div>

          <AppointmentCalendar />

          <div className="card bg-primary text-white border-0 mt-3 shadow-sm">
            <div className="card-body d-flex justify-content-between align-items-center">
              <div>
                <p className="fw-semibold mb-0">Get Started</p>
                <p className="small opacity-75 mb-0">View patient analytics</p>
              </div>
              <ArrowRight size={20} className="opacity-75" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;