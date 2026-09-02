import React, { useState } from 'react';
import api from '../api/axiosConfig';
import { Plus } from 'lucide-react';

const AddReadingModal = ({ patientId, patientName, onReadingAdded, onClose }) => {
  const [show, setShow] = useState(false);
  const [formData, setFormData] = useState({
    systolic: '',
    diastolic: '',
    pulse_rate: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload = {
        patient: patientId,
        systolic: parseInt(formData.systolic),
        diastolic: parseInt(formData.diastolic),
        pulse_rate: formData.pulse_rate ? parseInt(formData.pulse_rate) : null,
      };
      await api.post('/bp_readings/', payload);
      setShow(false);
      setFormData({ systolic: '', diastolic: '', pulse_rate: '' });
      if (onReadingAdded) onReadingAdded();
      if (onClose) onClose();
    } catch (err) {
      console.error('Error adding reading:', err);
      setError('Failed to add reading. Please check the values.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setShow(false);
    if (onClose) onClose();
  };

  return (
    <>
      <button className="btn btn-primary btn-sm" onClick={() => setShow(true)}>
        <Plus size={16} className="me-1" /> Add Reading
      </button>

      {show && (
        <div
          className="modal show d-block"
          role="dialog"
          aria-modal="true"
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
                <h5 className="modal-title">Add Reading for {patientName}</h5>
                <button className="btn-close" aria-label="Close" onClick={handleClose} />
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  {error && (
                    <div className="alert alert-danger py-1 small">{error}</div>
                  )}
                  <div className="mb-3">
                    <label htmlFor="systolic" className="form-label">Systolic (mmHg)</label>
                    <input
                      type="number"
                      className="form-control"
                      id="systolic"
                      name="systolic"
                      value={formData.systolic}
                      onChange={handleChange}
                      required
                      min="50"
                      max="250"
                      placeholder="e.g., 120"
                    />
                  </div>
                  <div className="mb-3">
                    <label htmlFor="diastolic" className="form-label">Diastolic (mmHg)</label>
                    <input
                      type="number"
                      className="form-control"
                      id="diastolic"
                      name="diastolic"
                      value={formData.diastolic}
                      onChange={handleChange}
                      required
                      min="30"
                      max="200"
                      placeholder="e.g., 80"
                    />
                  </div>
                  <div className="mb-3">
                    <label htmlFor="pulse_rate" className="form-label">Pulse Rate (optional)</label>
                    <input
                      type="number"
                      className="form-control"
                      id="pulse_rate"
                      name="pulse_rate"
                      value={formData.pulse_rate}
                      onChange={handleChange}
                      min="30"
                      max="220"
                      placeholder="e.g., 72"
                    />
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={handleClose}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Saving...' : 'Save'}
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

export default AddReadingModal;