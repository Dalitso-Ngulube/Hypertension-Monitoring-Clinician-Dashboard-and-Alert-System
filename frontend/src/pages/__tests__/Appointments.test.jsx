import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Appointments from '../Appointments';
import api from '../../api/axiosConfig';
import { AuthContext } from '../../context/AuthContext';

jest.mock('../../api/axiosConfig');

const mockUser = {
  id: 1,
  username: 'clinician1',
  role: 'clinician',
};

const mockAppointments = [
  {
    id: 1,
    patient_name: 'John Doe',
    date: '2026-06-23',
    time: '09:00:00',
    status: 'SCHEDULED',
  },
  {
    id: 2,
    patient_name: 'Jane Smith',
    date: '2026-06-24',
    time: '14:30:00',
    status: 'SCHEDULED',
  },
];

const renderWithContext = (component) => {
  return render(
    <BrowserRouter>
      <AuthContext.Provider value={{ user: mockUser, isAuthenticated: true }}>
        {component}
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('Appointments', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    renderWithContext(<Appointments />);
    expect(document.querySelector('.spinner-border')).toBeInTheDocument();
  });

  it('renders appointments list when data is available', async () => {
    api.get.mockResolvedValue({ data: { results: mockAppointments } });
    renderWithContext(<Appointments />);

    await waitFor(() => {
      expect(screen.getByText('Appointments')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('shows "No appointments" message when list is empty', async () => {
    api.get.mockResolvedValue({ data: { results: [] } });
    renderWithContext(<Appointments />);

    await waitFor(() => {
      expect(screen.getByText(/No appointments/i)).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    api.get.mockRejectedValue(new Error('Network error'));
    renderWithContext(<Appointments />);

    await waitFor(() => {
      expect(screen.getByText(/No appointments/i)).toBeInTheDocument();
    });
  });
});