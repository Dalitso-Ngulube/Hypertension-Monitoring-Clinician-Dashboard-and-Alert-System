import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosConfig';
import { Search, UserPlus, User, Mail, Phone, Calendar, ChevronLeft, Download, Eye, Plus } from 'lucide-react';
import AddPatientModal from '../components/AddPatientModal';
import AddReadingModal from '../components/AddReadingModal';
import MedicalHistory from '../components/MedicalHistory';
import BPHistoryTable from '../components/BPHistoryTable';

const Patients = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchPatients = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/patients/');
      setPatients(response.data.results || []);
    } catch (error) {
      console.error('Error fetching patients:', error);
      setError('Failed to load patients. Please try again.');
      setPatients([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [refreshKey]);

  const filteredPatients = patients.filter(p =>
    `${p.first_name} ${p.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.phone_number?.includes(searchTerm)
  );

  const isClinicianOrAdmin = user && (user.role === 'clinician' || user.role === 'admin');

  const handleRefresh = () => setRefreshKey(prev => prev + 1);

  if (selectedPatient) {
    return (
      <div className="container-fluid py-4">
        <button className="btn btn-link text-muted mb-3" onClick={() => setSelectedPatient(null)}>
          <ChevronLeft size={16} className="me-1" /> Back to Patients
        </button>
        <div className="card card-clinical mb-3">
          <div className="card-body">
            <div className="d-flex align-items-center gap-4">
              <div className="bg-primary bg-opacity-10 rounded-circle d-flex align-items-center justify-content-center" style={{ width: 56, height: 56 }}>
                <span className="fw-bold fs-3 text-primary">{selectedPatient.first_name?.[0]}{selectedPatient.last_name?.[0]}</span>
              </div>
              <div>
                <h4 className="fw-bold mb-0">{selectedPatient.first_name} {selectedPatient.last_name}</h4>
                <p className="text-muted small">ID: {String(selectedPatient.id).padStart(4, '0')} • Age: {selectedPatient.age}</p>
                <div className="d-flex flex-wrap gap-3 small text-secondary">
                  <span><Calendar size={14} className="me-1" /> Age: {selectedPatient.age}</span>
                  <span><User size={14} className="me-1" /> {selectedPatient.gender || 'Not specified'}</span>
                  <span><Phone size={14} className="me-1" /> {selectedPatient.phone_number || 'No phone'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <MedicalHistory patientId={selectedPatient.id} onUpdate={handleRefresh} />
        <BPHistoryTable patientId={selectedPatient.id} />
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <div>
          <h1 className="sidebar-page-heading fw-bold">Patients</h1>
          <p className="text-muted small">Manage your patient list</p>
        </div>
        {isClinicianOrAdmin && (
          <div className="d-flex gap-2">
            <button className="btn btn-outline-primary btn-sm" onClick={() => { const token = localStorage.getItem('access'); window.open(`http://localhost:8000/api/analytics/export/summary/?token=${token}`, '_blank'); }}>
              <Download size={16} className="me-1" /> Export Summary
            </button>
            <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
              <UserPlus size={16} className="me-1" /> Add Patient
            </button>
          </div>
        )}
      </div>

      <div className="input-group mb-4">
        <span className="input-group-text bg-white border-end-0"><Search size={16} className="text-muted" /></span>
        <input type="text" className="form-control border-start-0" placeholder="Search patients by name or phone..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
        <span className="input-group-text bg-white border-start-0 text-muted small">{filteredPatients.length} patients</span>
      </div>

      {loading && (
        <div className="text-center py-5" role="status">
          <div className="spinner-border text-primary" />
          <p className="mt-2 text-muted">Loading patients...</p>
        </div>
      )}

      {!loading && error && (
        <div className="alert alert-danger">{error}</div>
      )}

      {!loading && !error && filteredPatients.length === 0 && (
        <div className="card card-clinical text-center py-5">
          <User size={48} className="mx-auto text-muted mb-3" />
          <h5>No Patients</h5>
          <p className="text-muted small">Add your first patient to get started.</p>
        </div>
      )}

      {!loading && !error && filteredPatients.length > 0 && (
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead className="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Phone</th>
                <th>Email</th>
                <th className="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPatients.map((p) => (
                <tr key={p.id}>
                  <td>#{String(p.id).padStart(4, '0')}</td>
                  <td>
                    <div className="d-flex align-items-center gap-2">
                      <div className="bg-primary bg-opacity-10 rounded-circle d-flex align-items-center justify-content-center" style={{ width: 32, height: 32 }}>
                        <span className="fw-bold small text-primary">{p.first_name?.[0]}{p.last_name?.[0]}</span>
                      </div>
                      <span className="fw-semibold">{p.first_name} {p.last_name}</span>
                    </div>
                  </td>
                  <td>{p.age}</td>
                  <td>{p.gender || '—'}</td>
                  <td>{p.phone_number || '—'}</td>
                  <td>{p.user?.email || '—'}</td>
                  <td className="text-center">
                    <div className="d-flex justify-content-center gap-1">
                      <button className="btn btn-sm btn-outline-primary" onClick={() => setSelectedPatient(p)}>
                        <Eye size={14} className="me-1" /> Details
                      </button>
                      <AddReadingModal
                        patientId={p.id}
                        patientName={`${p.first_name} ${p.last_name}`}
                        onReadingAdded={handleRefresh}
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <AddPatientModal
          onPatientAdded={(newPatient) => {
            setShowModal(false);
            handleRefresh();
            navigate(`/patients/${newPatient.id}`);
          }}
        />
      )}
    </div>
  );
};

export default Patients;