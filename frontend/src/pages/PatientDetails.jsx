import React, { useState, useEffect, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosConfig';
import MedicalHistory from '../components/MedicalHistory';
import BPHistoryTable from '../components/BPHistoryTable';
import { User, Mail, Phone, Calendar, MapPin, Activity } from 'lucide-react';

const PatientDetails = () => {
  const { id } = useParams();
  const { user } = useContext(AuthContext);
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showHistory, setShowHistory] = useState(true);

  useEffect(() => {
    const fetchPatient = async () => {
      try {
        const response = await api.get(`/patients/${id}/`);
        setPatient(response.data);
      } catch (error) {
        console.error('Error fetching patient:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchPatient();
  }, [id]);

  if (loading) return <div className="text-center py-8 text-slate-400">Loading patient details...</div>;
  if (!patient) return <div className="text-center py-8 text-slate-400">Patient not found.</div>;

  return (
    <div className="patient-details-page dashboard-bg">
      {/* Patient Info Card */}
      <div className="card-soft">
        <div className="card-body">
          <div className="flex flex-wrap items-start gap-6">
            <div className="w-20 h-20 rounded-full bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center text-teal-600 dark:text-teal-400 text-3xl font-bold">
              {patient.first_name?.[0]}{patient.last_name?.[0]}
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-slate-800 dark:text-white">
                {patient.first_name} {patient.last_name}
              </h2>
              <p className="text-sm text-slate-400">Patient ID: {String(patient.id).padStart(4, '0')}</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3 text-sm text-slate-600 dark:text-slate-300">
                <div className="flex items-center gap-2"><Calendar size={14} /> Age: {patient.age}</div>
                <div className="flex items-center gap-2"><User size={14} /> Gender: {patient.gender || 'Not specified'}</div>
                <div className="flex items-center gap-2"><Phone size={14} /> {patient.phone_number || 'No phone'}</div>
                <div className="flex items-center gap-2"><Mail size={14} /> {patient.user?.email || 'No email'}</div>
                <div className="flex items-center gap-2 sm:col-span-2"><MapPin size={14} /> {patient.address || 'No address'}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Toggle for BP History */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-800 dark:text-white flex items-center gap-2">
          <Activity size={20} className="text-teal-500" />
          BP History & Averages
        </h3>
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="text-sm text-teal-600 hover:text-teal-700 dark:text-teal-400 dark:hover:text-teal-300"
        >
          {showHistory ? 'Hide' : 'Show'} History
        </button>
      </div>

      {showHistory && <BPHistoryTable patientId={patient.id} />}

      {/* Medical History */}
      <div className="mt-8">
        <MedicalHistory patientId={patient.id} />
      </div>
    </div>
  );
};

export default PatientDetails;