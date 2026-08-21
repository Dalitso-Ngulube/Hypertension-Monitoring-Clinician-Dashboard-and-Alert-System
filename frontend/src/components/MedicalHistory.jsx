import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axiosConfig';
import { Save, Activity, Pill, Stethoscope, Heart, User, Phone, Calendar, AlertCircle } from 'lucide-react';

const MedicalHistory = ({ patientId, onUpdate }) => {
  const { user } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [conditions, setConditions] = useState([]);
  const [allergies, setAllergies] = useState([]);
  const [medications, setMedications] = useState([]);
  const [selectedConditions, setSelectedConditions] = useState([]);
  const [selectedAllergies, setSelectedAllergies] = useState([]);
  const [selectedMedications, setSelectedMedications] = useState([]);
  const [formData, setFormData] = useState({
    condition_notes: '', allergy_notes: '', current_medication_notes: '',
    has_diabetes: false, has_kidney_disease: false, has_heart_disease: false, has_stroke_history: false, comorbidity_notes: '',
    emergency_name: '', emergency_phone: '', emergency_relationship: '',
    smoking_status: 'NEVER', smoking_pack_years: '', alcohol_consumption: 'NONE',
    physical_activity: 'SEDENTARY', diet_description: '',
    family_history_hypertension: false, family_history_diabetes: false,
    family_history_heart_disease: false, family_history_stroke: false, family_history_notes: '',
    bmi: '',
  });

  const isClinicianOrAdmin = user && (user.role === 'clinician' || user.role === 'admin');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const historyRes = await api.get(`/patients/${patientId}/medical-history/`);
        setSelectedConditions(historyRes.data.conditions?.map(c => c.id) || []);
        setSelectedAllergies(historyRes.data.allergies?.map(a => a.id) || []);
        setSelectedMedications(historyRes.data.current_medications?.map(m => m.id) || []);
        setFormData({
          condition_notes: historyRes.data.condition_notes || '',
          allergy_notes: historyRes.data.allergy_notes || '',
          current_medication_notes: historyRes.data.current_medication_notes || '',
          has_diabetes: historyRes.data.has_diabetes || false,
          has_kidney_disease: historyRes.data.has_kidney_disease || false,
          has_heart_disease: historyRes.data.has_heart_disease || false,
          has_stroke_history: historyRes.data.has_stroke_history || false,
          comorbidity_notes: historyRes.data.comorbidity_notes || '',
          emergency_name: historyRes.data.emergency_name || '',
          emergency_phone: historyRes.data.emergency_phone || '',
          emergency_relationship: historyRes.data.emergency_relationship || '',
          smoking_status: historyRes.data.smoking_status || 'NEVER',
          smoking_pack_years: historyRes.data.smoking_pack_years || '',
          alcohol_consumption: historyRes.data.alcohol_consumption || 'NONE',
          physical_activity: historyRes.data.physical_activity || 'SEDENTARY',
          diet_description: historyRes.data.diet_description || '',
          family_history_hypertension: historyRes.data.family_history_hypertension || false,
          family_history_diabetes: historyRes.data.family_history_diabetes || false,
          family_history_heart_disease: historyRes.data.family_history_heart_disease || false,
          family_history_stroke: historyRes.data.family_history_stroke || false,
          family_history_notes: historyRes.data.family_history_notes || '',
          bmi: historyRes.data.bmi || '',
        });

        // Fetch reference data with safe array handling
        const [condRes, allergyRes, medRes] = await Promise.all([
          api.get('/patients/reference/conditions/'),
          api.get('/patients/reference/allergies/'),
          api.get('/patients/reference/medications/'),
        ]);

        // Ensure we extract arrays (handle paginated responses)
        setConditions(
          Array.isArray(condRes.data) ? condRes.data :
          Array.isArray(condRes.data?.results) ? condRes.data.results : []
        );
        setAllergies(
          Array.isArray(allergyRes.data) ? allergyRes.data :
          Array.isArray(allergyRes.data?.results) ? allergyRes.data.results : []
        );
        setMedications(
          Array.isArray(medRes.data) ? medRes.data :
          Array.isArray(medRes.data?.results) ? medRes.data.results : []
        );
      } catch (error) {
        console.error('Error fetching medical history:', error);
        // Set empty arrays on error to prevent crashes
        setConditions([]);
        setAllergies([]);
        setMedications([]);
      } finally {
        setLoading(false);
      }
    };
    if (patientId && isClinicianOrAdmin) fetchData();
  }, [patientId, isClinicianOrAdmin]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put(`/patients/${patientId}/medical-history/`, {
        ...formData,
        condition_ids: selectedConditions,
        allergy_ids: selectedAllergies,
        medication_ids: selectedMedications,
      });
      if (onUpdate) onUpdate();
      alert('Medical history saved successfully!');
    } catch (error) {
      console.error(error);
      alert('Failed to save medical history.');
    } finally {
      setSaving(false);
    }
  };

  const handleMultiSelect = (e, setter) => {
    const options = e.target.options;
    const values = [];
    for (let i = 0; i < options.length; i++) {
      if (options[i].selected) values.push(parseInt(options[i].value));
    }
    setter(values);
  };

  if (loading) return <div className="text-center py-4 text-muted">Loading medical history...</div>;
  if (!isClinicianOrAdmin) return <div className="text-center py-4 text-muted">You don't have permission to view medical history.</div>;

  return (
    <div className="card card-clinical">
      <div className="card-header d-flex justify-content-between align-items-center">
        <span><Activity size={16} className="me-2" /> Medical History</span>
        <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>
          <Save size={14} className="me-1" /> {saving ? 'Saving...' : 'Save'}
        </button>
      </div>
      <div className="card-body">
        <div className="row g-3">
          <div className="col-md-6">
            <label className="form-label small fw-semibold text-muted text-uppercase"><Stethoscope size={14} className="me-1" /> Conditions</label>
            <select
              multiple
              className="form-select form-select-sm"
              value={selectedConditions}
              onChange={(e) => handleMultiSelect(e, setSelectedConditions)}
              style={{ height: '100px' }}
            >
              {Array.isArray(conditions) && conditions.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
            <input
              type="text"
              className="form-control form-control-sm mt-1"
              placeholder="Condition notes..."
              value={formData.condition_notes}
              onChange={(e) => setFormData({ ...formData, condition_notes: e.target.value })}
            />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold text-muted text-uppercase"><AlertCircle size={14} className="me-1" /> Allergies</label>
            <select
              multiple
              className="form-select form-select-sm"
              value={selectedAllergies}
              onChange={(e) => handleMultiSelect(e, setSelectedAllergies)}
              style={{ height: '100px' }}
            >
              {Array.isArray(allergies) && allergies.map(a => (
                <option key={a.id} value={a.id}>{a.name} ({a.severity})</option>
              ))}
            </select>
            <input
              type="text"
              className="form-control form-control-sm mt-1"
              placeholder="Allergy notes..."
              value={formData.allergy_notes}
              onChange={(e) => setFormData({ ...formData, allergy_notes: e.target.value })}
            />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold text-muted text-uppercase"><Pill size={14} className="me-1" /> Current Medications</label>
            <select
              multiple
              className="form-select form-select-sm"
              value={selectedMedications}
              onChange={(e) => handleMultiSelect(e, setSelectedMedications)}
              style={{ height: '100px' }}
            >
              {Array.isArray(medications) && medications.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
            <input
              type="text"
              className="form-control form-control-sm mt-1"
              placeholder="Dosage, frequency..."
              value={formData.current_medication_notes}
              onChange={(e) => setFormData({ ...formData, current_medication_notes: e.target.value })}
            />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold text-muted text-uppercase"><Heart size={14} className="me-1" /> Comorbidities</label>
            <div className="d-flex flex-wrap gap-2">
              {['has_diabetes', 'has_kidney_disease', 'has_heart_disease', 'has_stroke_history'].map(key => (
                <div key={key} className="form-check form-check-inline">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={formData[key]}
                    onChange={(e) => setFormData({ ...formData, [key]: e.target.checked })}
                  />
                  <label className="form-check-label small">{key.replace('has_', '').replace('_', ' ').toUpperCase()}</label>
                </div>
              ))}
            </div>
            <input
              type="text"
              className="form-control form-control-sm mt-1"
              placeholder="Comorbidity notes..."
              value={formData.comorbidity_notes}
              onChange={(e) => setFormData({ ...formData, comorbidity_notes: e.target.value })}
            />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold text-muted text-uppercase"><Phone size={14} className="me-1" /> Emergency Contact</label>
            <input
              type="text"
              className="form-control form-control-sm mb-1"
              placeholder="Name"
              value={formData.emergency_name}
              onChange={(e) => setFormData({ ...formData, emergency_name: e.target.value })}
            />
            <input
              type="text"
              className="form-control form-control-sm mb-1"
              placeholder="Phone"
              value={formData.emergency_phone}
              onChange={(e) => setFormData({ ...formData, emergency_phone: e.target.value })}
            />
            <input
              type="text"
              className="form-control form-control-sm"
              placeholder="Relationship"
              value={formData.emergency_relationship}
              onChange={(e) => setFormData({ ...formData, emergency_relationship: e.target.value })}
            />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold text-muted text-uppercase"><User size={14} className="me-1" /> Lifestyle</label>
            <select
              className="form-select form-select-sm mb-1"
              value={formData.smoking_status}
              onChange={(e) => setFormData({ ...formData, smoking_status: e.target.value })}
            >
              <option value="NEVER">Never Smoked</option>
              <option value="FORMER">Former Smoker</option>
              <option value="CURRENT">Current Smoker</option>
            </select>
            {formData.smoking_status === 'CURRENT' && (
              <input
                type="number"
                className="form-control form-control-sm mb-1"
                placeholder="Pack-years"
                value={formData.smoking_pack_years}
                onChange={(e) => setFormData({ ...formData, smoking_pack_years: e.target.value })}
              />
            )}
            <select
              className="form-select form-select-sm mb-1"
              value={formData.alcohol_consumption}
              onChange={(e) => setFormData({ ...formData, alcohol_consumption: e.target.value })}
            >
              <option value="NONE">No Alcohol</option>
              <option value="LIGHT">Light (1-2 drinks/week)</option>
              <option value="MODERATE">Moderate (3-14 drinks/week)</option>
              <option value="HEAVY">Heavy (more than 14 drinks/week)</option>
            </select>
            <select
              className="form-select form-select-sm mb-1"
              value={formData.physical_activity}
              onChange={(e) => setFormData({ ...formData, physical_activity: e.target.value })}
            >
              <option value="SEDENTARY">Sedentary</option>
              <option value="LIGHT">Light</option>
              <option value="MODERATE">Moderate</option>
              <option value="ACTIVE">Active</option>
            </select>
            <input
              type="number"
              className="form-control form-control-sm mb-1"
              placeholder="BMI"
              step="0.1"
              value={formData.bmi}
              onChange={(e) => setFormData({ ...formData, bmi: e.target.value })}
            />
            <textarea
              className="form-control form-control-sm"
              placeholder="Diet description..."
              rows="1"
              value={formData.diet_description}
              onChange={(e) => setFormData({ ...formData, diet_description: e.target.value })}
            />
          </div>
          <div className="col-12">
            <label className="form-label small fw-semibold text-muted text-uppercase"><Calendar size={14} className="me-1" /> Family History</label>
            <div className="d-flex flex-wrap gap-2">
              {['hypertension', 'diabetes', 'heart_disease', 'stroke'].map(key => (
                <div key={key} className="form-check form-check-inline">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={formData[`family_history_${key}`]}
                    onChange={(e) => setFormData({ ...formData, [`family_history_${key}`]: e.target.checked })}
                  />
                  <label className="form-check-label small">{key.replace('_', ' ').toUpperCase()}</label>
                </div>
              ))}
            </div>
            <input
              type="text"
              className="form-control form-control-sm mt-1"
              placeholder="Family history notes..."
              value={formData.family_history_notes}
              onChange={(e) => setFormData({ ...formData, family_history_notes: e.target.value })}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MedicalHistory;