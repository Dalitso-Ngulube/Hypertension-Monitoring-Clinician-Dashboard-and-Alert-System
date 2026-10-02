import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../Dashboard';
import { AuthContext } from '../../context/AuthContext';
import api from '../../api/axiosConfig';

jest.mock('../../api/axiosConfig');

const mockUser = {
  id: 1,
  username: 'clinician1',
  role: 'clinician',
};

const mockPatients = [
  { id: 1, first_name: 'John', last_name: 'Doe' },
  { id: 2, first_name: 'Jane', last_name: 'Smith' },
];

const mockReadings = [
  { id: 1, systolic: 140, diastolic: 90, risk_category: 'STAGE_2', recorded_at: '2026-06-23T10:00:00Z' },
  { id: 2, systolic: 120, diastolic: 80, risk_category: 'NORMAL', recorded_at: '2026-06-22T10:00:00Z' },
];

const renderWithContext = (component, user = mockUser) => {
  return render(
    <BrowserRouter>
      <AuthContext.Provider value={{ user, isAuthenticated: true, logout: jest.fn() }}>
        {component}
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('Dashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders greeting with username', async () => {
    api.get
      .mockResolvedValueOnce({ data: { results: mockPatients } })
      .mockResolvedValueOnce({ data: mockReadings })
      .mockResolvedValueOnce({ data: { results: mockPatients } })
      .mockResolvedValueOnce({ data: { results: mockReadings } });

    renderWithContext(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Good (morning|afternoon|evening), clinician1/i)).toBeInTheDocument();
    });
  });

  it('displays patient statistics', async () => {
    api.get
      .mockResolvedValueOnce({ data: { results: mockPatients } })
      .mockResolvedValueOnce({ data: mockReadings })
      .mockResolvedValueOnce({ data: { results: mockPatients } })
      .mockResolvedValueOnce({ data: { results: mockReadings } });

    renderWithContext(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Patients')).toBeInTheDocument();
      const patientCount = screen.getAllByText('2')[0];
      expect(patientCount).toBeInTheDocument();
      expect(screen.getByText('Readings')).toBeInTheDocument();
      const readingCount = screen.getAllByText('0')[0];
      expect(readingCount).toBeInTheDocument();
    });
  });

  it('renders PatientSelector and TrendChart', async () => {
    api.get
      .mockResolvedValueOnce({ data: { results: mockPatients } })
      .mockResolvedValueOnce({ data: mockReadings })
      .mockResolvedValueOnce({ data: { results: mockPatients } })
      .mockResolvedValueOnce({ data: { results: mockReadings } });

    renderWithContext(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });
  });
});