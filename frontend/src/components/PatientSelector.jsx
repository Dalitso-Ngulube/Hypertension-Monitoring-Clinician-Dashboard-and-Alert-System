import React, { useState, useEffect } from 'react';
import api from '../api/axiosConfig';

const PatientSelector = ({ onSelectPatient }) => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllPatients = async () => {
      try {
        let allPatients = [];
        let nextUrl = '/patients/';
        while (nextUrl) {
          const response = await api.get(nextUrl);
          allPatients = [...allPatients, ...(response.data.results || [])];
          nextUrl = response.data.next;
        }
        setPatients(allPatients);
      } catch (error) { console.error(error); } finally { setLoading(false); }
    };
    fetchAllPatients();
  }, []);

  if (loading) return <div className="text-muted small">Loading patients...</div>;

  return (
    <div>
      <label className="form-label small text-uppercase fw-semibold text-muted">Select Patient</label>
      <select className="form-select form-select-sm" onChange={(e) => onSelectPatient(parseInt(e.target.value))} defaultValue="">
        <option value="">-- Choose a patient --</option>
        {patients.map(p => <option key={p.id} value={p.id}>{p.first_name} {p.last_name} (Age: {p.age})</option>)}
      </select>
    </div>
  );
};

export default PatientSelector;