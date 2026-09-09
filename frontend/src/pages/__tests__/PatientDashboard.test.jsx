import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PatientDashboard from '../PatientDashboard';
import api from '../../api/axiosConfig';
import { AuthContext } from '../../context/AuthContext';

jest.mock('../../api/axiosConfig');
jest.mock('../../components/BPHistoryTable', () => () => <div>BP history</div>);
jest.mock('react-chartjs-2', () => ({
  Line: () => null,
}));

const mockUser = {
  id: 1,
  username: 'patient1',
  role: 'patient',
};

const mockReadings = [
  { id: 1, systolic: 140, diastolic: 90, pulse_rate: 72, recorded_at: '2026-06-23T10:00:00Z', risk_category: 'STAGE_2' },
  { id: 2, systolic: 120, diastolic: 80, pulse_rate: 68, recorded_at: '2026-06-22T10:00:00Z', risk_category: 'NORMAL' },
];

const mockSummary = {
  total_readings: 2,
  total_patients: 1,
  critical_readings: 0,
};

const renderWithContext = (component) => {
  return render(
    <AuthContext.Provider value={{ user: mockUser, isAuthenticated: true }}>
      {component}
    </AuthContext.Provider>
  );
};

describe('PatientDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders dashboard with stats and chart', async () => {
    api.get
      .mockResolvedValueOnce({ data: { results: mockReadings } })
      .mockResolvedValueOnce({ data: mockSummary });

    renderWithContext(<PatientDashboard />);

    await waitFor(() => {
      expect(screen.getByText('My Health Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Welcome back, patient1')).toBeInTheDocument();
      expect(screen.getByText('Latest BP')).toBeInTheDocument();
      expect(screen.getByText('140/90')).toBeInTheDocument();
      expect(screen.getByText('Total Readings')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
    });
  });

  it('opens Add Reading modal when floating button is clicked', async () => {
    api.get
      .mockResolvedValueOnce({ data: { results: mockReadings } })
      .mockResolvedValueOnce({ data: mockSummary });

    renderWithContext(<PatientDashboard />);

    await waitFor(() => {
      const addButton = document.querySelector('.btn-primary.rounded-circle');
      fireEvent.click(addButton);
    });

    expect(screen.getByText('Add Blood Pressure Reading')).toBeInTheDocument();
  });

  it('adds a new reading when form is submitted', async () => {
    api.get
      .mockResolvedValueOnce({ data: { results: mockReadings } })
      .mockResolvedValueOnce({ data: mockSummary });
    
    api.post.mockResolvedValue({ data: {} });

    renderWithContext(<PatientDashboard />);

    await waitFor(() => {
      const addButton = document.querySelector('.btn-primary.rounded-circle');
      fireEvent.click(addButton);
    });

    const systolicInput = screen.getByPlaceholderText('e.g., 120');
    const diastolicInput = screen.getByPlaceholderText('e.g., 80');

    fireEvent.change(systolicInput, { target: { value: '130' } });
    fireEvent.change(diastolicInput, { target: { value: '85' } });
    
    const form = document.querySelector('form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/bp_readings/patient/add/', {
        systolic: '130',
        diastolic: '85',
        pulse_rate: '',
      });
    });
  });

  it('shows "Access denied" for non-patients', () => {
    const nonPatientUser = { ...mockUser, role: 'clinician' };
    render(
      <AuthContext.Provider value={{ user: nonPatientUser, isAuthenticated: true }}>
        <PatientDashboard />
      </AuthContext.Provider>
    );
    expect(screen.getByText(/Access denied/i)).toBeInTheDocument();
  });
});