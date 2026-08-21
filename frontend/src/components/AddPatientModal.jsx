import React, { useState } from 'react';
import api from '../api/axiosConfig';
import { X, UserPlus, HeartPulse } from 'lucide-react';

const AddPatientModal = ({ onPatientAdded }) => {
  const [show, setShow] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    age: '',
    gender: '',
    phone_number: '',
    address: '',
    height: '',
    weight: '',
    systolic: '',
    diastolic: '',
    pulse_rate: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // 1. Create the patient
      const patientPayload = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        age: parseInt(formData.age),
        gender: formData.gender || null,
        phone_number: formData.phone_number || '',
        address: formData.address || '',
        height: formData.height ? parseFloat(formData.height) : null,
        weight: formData.weight ? parseFloat(formData.weight) : null,
      };
      const patientResponse = await api.post('/patients/', patientPayload);
      const newPatient = patientResponse.data;

      // 2. If BP fields are provided, add a reading
      if (formData.systolic && formData.diastolic) {
        const readingPayload = {
          patient: newPatient.id,
          systolic: parseInt(formData.systolic),
          diastolic: parseInt(formData.diastolic),
          pulse_rate: formData.pulse_rate ? parseInt(formData.pulse_rate) : null,
        };
        await api.post('/bp_readings/', readingPayload);
      }

      // 3. Close modal, clear form, and notify parent
      setShow(false);
      setFormData({
        first_name: '',
        last_name: '',
        age: '',
        gender: '',
        phone_number: '',
        address: '',
        height: '',
        weight: '',
        systolic: '',
        diastolic: '',
        pulse_rate: '',
      });
      if (onPatientAdded) onPatientAdded(newPatient);

    } catch (err) {
      console.error('Error adding patient:', err);
      setError('Failed to add patient. Please check the form.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button className="btn btn-primary btn-sm" onClick={() => setShow(true)}>
        <UserPlus size={16} className="me-1" /> Add Patient
      </button>

      {show && (
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
          <div className="modal-dialog modal-dialog-centered modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Add New Patient</h5>
                <button className="btn-close" onClick={() => setShow(false)} />
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  {error && (
                    <div className="alert alert-danger py-1 small">{error}</div>
                  )}
                  <div className="row g-3">
                    {/* Demographics */}
                    <div className="col-md-6">
                      <label className="form-label">First Name</label>
                      <input
                        type="text"
                        className="form-control"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleChange}
                        required
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">Last Name</label>
                      <input
                        type="text"
                        className="form-control"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                        required
                      />
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">Age</label>
                      <input
                        type="number"
                        className="form-control"
                        name="age"
                        value={formData.age}
                        onChange={handleChange}
                        required
                      />
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">Gender</label>
                      <select
                        className="form-select"
                        name="gender"
                        value={formData.gender}
                        onChange={handleChange}
                      >
                        <option value="">Select</option>
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                      </select>
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">Phone</label>
                      <input
                        type="text"
                        className="form-control"
                        name="phone_number"
                        value={formData.phone_number}
                        onChange={handleChange}
                      />
                    </div>
                    <div className="col-12">
                      <label className="form-label">Address</label>
                      <textarea
                        className="form-control"
                        name="address"
                        value={formData.address}
                        onChange={handleChange}
                        rows="2"
                      />
                    </div>

                    {/* Height & Weight */}
                    <div className="col-md-6">
                      <label className="form-label">Height (m)</label>
                      <input
                        type="number"
                        step="0.01"
                        className="form-control"
                        name="height"
                        placeholder="e.g., 1.75"
                        value={formData.height}
                        onChange={handleChange}
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">Weight (kg)</label>
                      <input
                        type="number"
                        step="0.1"
                        className="form-control"
                        name="weight"
                        placeholder="e.g., 72.5"
                        value={formData.weight}
                        onChange={handleChange}
                      />
                    </div>

                    {/* BP Reading (optional) */}
                    <div className="col-12">
                      <hr className="my-1" />
                      <label className="fw-semibold small text-muted text-uppercase">
                        <HeartPulse size={14} className="me-1" /> Initial BP Reading (optional)
                      </label>
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">Systolic (mmHg)</label>
                      <input
                        type="number"
                        className="form-control"
                        name="systolic"
                        placeholder="e.g., 120"
                        value={formData.systolic}
                        onChange={handleChange}
                        min="50"
                        max="250"
                      />
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">Diastolic (mmHg)</label>
                      <input
                        type="number"
                        className="form-control"
                        name="diastolic"
                        placeholder="e.g., 80"
                        value={formData.diastolic}
                        onChange={handleChange}
                        min="30"
                        max="200"
                      />
                    </div>
                    <div className="col-md-4">
                      <label className="form-label">Pulse Rate (optional)</label>
                      <input
                        type="number"
                        className="form-control"
                        name="pulse_rate"
                        placeholder="e.g., 72"
                        value={formData.pulse_rate}
                        onChange={handleChange}
                        min="30"
                        max="220"
                      />
                    </div>
                  </div>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShow(false)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? 'Saving...' : 'Add Patient'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AddPatientModal;