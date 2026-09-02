import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthContext } from '../../context/AuthContext';
import MedicalHistory from '../MedicalHistory';
import api from '../../api/axiosConfig';

jest.mock('../../api/axiosConfig', () => ({
  get: jest.fn(),
  put: jest.fn(),
}));

const renderWithContext = (component, user) => {
  return render(
    <AuthContext.Provider value={{ user, token: 'mock-token' }}>
      {component}
    </AuthContext.Provider>
  );
};

describe('MedicalHistory', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockHistoryData = {
    conditions: [],
    allergies: [],
    current_medications: [],
    condition_notes: '',
    allergy_notes: '',
    current_medication_notes: '',
    has_diabetes: false,
    has_kidney_disease: false,
    has_heart_disease: false,
    has_stroke_history: false,
    comorbidity_notes: '',
    emergency_name: '',
    emergency_phone: '',
    emergency_relationship: '',
    smoking_status: 'NEVER',
    smoking_pack_years: '',
    alcohol_consumption: 'NONE',
    physical_activity: 'SEDENTARY',
    diet_description: '',
    family_history_hypertension: false,
    family_history_diabetes: false,
    family_history_heart_disease: false,
    family_history_stroke: false,
    family_history_notes: '',
    bmi: '',
  };

  const mockReferenceData = {
    conditions: [],
    allergies: [],
    medications: [],
  };

  it('shows loading state initially', async () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    renderWithContext(<MedicalHistory patientId={1} />, { role: 'clinician' });
    expect(screen.getByText(/Loading medical history/i)).toBeInTheDocument();
  });

  it('shows permission denied for non-clinicians', async () => {
    renderWithContext(<MedicalHistory patientId={1} />, { role: 'patient' });
    const permissionMessage = await screen.findByText(/You don't have permission/i);
    expect(permissionMessage).toBeInTheDocument();
  });

  it('renders form for clinicians', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockHistoryData })
      .mockResolvedValueOnce({ data: mockReferenceData.conditions })
      .mockResolvedValueOnce({ data: mockReferenceData.allergies })
      .mockResolvedValueOnce({ data: mockReferenceData.medications });

    renderWithContext(<MedicalHistory patientId={1} />, { role: 'clinician' });

    await waitFor(() => {
      expect(screen.getByText(/Medical History/i)).toBeInTheDocument();
    });
    expect(screen.getByText('Save')).toBeInTheDocument();
  });
});