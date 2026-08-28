import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MedicalHistory from '../MedicalHistory';
import api from '../../api/axiosConfig';
import { AuthContext } from '../../context/AuthContext';

jest.mock('../../api/axiosConfig');

const mockUser = {
  id: 1,
  username: 'clinician1',
  role: 'clinician',
};

const mockHistory = {
  id: 1,
  conditions: [{ id: 1, name: 'Diabetes' }],
  allergies: [{ id: 1, name: 'Penicillin' }],
  current_medications: [{ id: 1, name: 'Lisinopril' }],
  has_diabetes: true,
  has_kidney_disease: false,
  smoking_status: 'NEVER',
  alcohol_consumption: 'LIGHT',
  physical_activity: 'MODERATE',
  emergency_name: 'Jane Doe',
  emergency_phone: '555-555-5555',
};

const mockConditions = [{ id: 1, name: 'Diabetes' }, { id: 2, name: 'Hypertension' }];
const mockAllergies = [{ id: 1, name: 'Penicillin' }, { id: 2, name: 'Sulfa' }];
const mockMedications = [{ id: 1, name: 'Lisinopril' }, { id: 2, name: 'Amlodipine' }];

const renderWithContext = (component, user = mockUser) => {
  return render(
    <AuthContext.Provider value={{ user, isAuthenticated: true }}>
      {component}
    </AuthContext.Provider>
  );
};

describe('MedicalHistory', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.alert = jest.fn();
  });

  it('renders loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    renderWithContext(<MedicalHistory patientId={1} />);
    expect(screen.getByText(/Loading medical history/i)).toBeInTheDocument();
  });

  it('renders medical history form when data is loaded', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockHistory })
      .mockResolvedValueOnce({ data: mockConditions })
      .mockResolvedValueOnce({ data: mockAllergies })
      .mockResolvedValueOnce({ data: mockMedications });

    renderWithContext(<MedicalHistory patientId={1} />);

    await waitFor(() => {
      expect(screen.getByText('Medical History')).toBeInTheDocument();
      expect(screen.getByText('Conditions')).toBeInTheDocument();
      expect(screen.getByText('Allergies')).toBeInTheDocument();
      expect(screen.getByText('Current Medications')).toBeInTheDocument();
      expect(screen.getByText('Comorbidities')).toBeInTheDocument();
      expect(screen.getByText('Lifestyle')).toBeInTheDocument();
    });
  });

  it('saves history when Save button is clicked', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockHistory })
      .mockResolvedValueOnce({ data: mockConditions })
      .mockResolvedValueOnce({ data: mockAllergies })
      .mockResolvedValueOnce({ data: mockMedications });
    
    api.put.mockResolvedValue({ data: {} });

    renderWithContext(<MedicalHistory patientId={1} />);

    await waitFor(() => {
      const saveButton = screen.getByText('Save');
      fireEvent.click(saveButton);
    });

    expect(api.put).toHaveBeenCalledWith(
      '/patients/1/medical-history/',
      expect.any(Object)
    );
  });

  it('shows permission denied for non-clinicians', async () => {
    const patientUser = { ...mockUser, role: 'patient' };
    renderWithContext(<MedicalHistory patientId={1} />, patientUser);

    const permissionMessage = await screen.findByText(
      (content, element) => {
        return element.textContent.includes('permission') || 
               element.textContent.includes('access');
      },
      { timeout: 2000 }
    );
    expect(permissionMessage).toBeInTheDocument();
  });

  it('handles API error when saving', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockHistory })
      .mockResolvedValueOnce({ data: mockConditions })
      .mockResolvedValueOnce({ data: mockAllergies })
      .mockResolvedValueOnce({ data: mockMedications });
    
    api.put.mockRejectedValue(new Error('Network error'));

    renderWithContext(<MedicalHistory patientId={1} />);

    await waitFor(() => {
      const saveButton = screen.getByText('Save');
      fireEvent.click(saveButton);
    });

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalled();
    });
  });
});