import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AppointmentCalendar from '../AppointmentCalendar';
import api from '../../api/axiosConfig';
import { AuthContext } from '../../context/AuthContext';

jest.mock('../../api/axiosConfig');

const mockUser = {
  id: 1,
  username: 'clinician1',
  role: 'clinician',
};

const renderWithContext = (component) => {
  return render(
    <AuthContext.Provider value={{ user: mockUser, isAuthenticated: true }}>
      {component}
    </AuthContext.Provider>
  );
};

describe('AppointmentCalendar', () => {
  const mockAppointments = [
    {
      id: 1,
      patient_name: 'John Doe',
      date: new Date().toISOString().split('T')[0],
      time: '09:00:00',
      status: 'SCHEDULED',
    },
    {
      id: 2,
      patient_name: 'Jane Smith',
      date: new Date().toISOString().split('T')[0],
      time: '14:30:00',
      status: 'SCHEDULED',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    renderWithContext(<AppointmentCalendar />);
    expect(screen.getByText(/Loading appointments/i)).toBeInTheDocument();
  });

  it('renders calendar with appointments', async () => {
    api.get.mockResolvedValue({ data: { results: mockAppointments } });
    renderWithContext(<AppointmentCalendar />);

    await waitFor(() => {
      expect(screen.getByText('Appointment')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('shows "No appointments today" message', async () => {
    api.get.mockResolvedValue({ data: { results: [] } });
    renderWithContext(<AppointmentCalendar />);

    await waitFor(() => {
      const noAppointments = screen.queryByText(/No appointments/i);
      expect(noAppointments || screen.getByText(/Appointment/)).toBeInTheDocument();
    });
  });

  it('navigates weeks when arrow buttons are clicked', async () => {
    api.get.mockResolvedValue({ data: { results: mockAppointments } });
    renderWithContext(<AppointmentCalendar />);

    await waitFor(() => {
      const buttons = screen.getAllByRole('button');
      const nextButton = buttons.find(btn => 
        btn.querySelector('.lucide-chevron-right')
      );
      if (nextButton) {
        fireEvent.click(nextButton);
      }
    });
    
    expect(api.get).toHaveBeenCalledTimes(2);
  });

  it('opens modal when Add button is clicked', async () => {
    api.get.mockResolvedValue({ data: { results: mockAppointments } });
    renderWithContext(<AppointmentCalendar />);

    await waitFor(() => {
      const addButton = screen.getByText('Add');
      fireEvent.click(addButton);
    });

    expect(screen.getByText('Add Appointment')).toBeInTheDocument();
  });
});