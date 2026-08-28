import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AlertsList from '../AlertsList';
import api from '../../api/axiosConfig';
import { AuthContext } from '../../context/AuthContext';

jest.mock('../../api/axiosConfig');

const renderWithContext = (component) => {
  const mockUser = { id: 1, role: 'clinician' };
  return render(
    <AuthContext.Provider value={{ user: mockUser, isAuthenticated: true }}>
      {component}
    </AuthContext.Provider>
  );
};

describe('AlertsList', () => {
  const mockAlerts = [
    {
      id: 1,
      patient_name: 'John Doe',
      severity: 'CRITICAL',
      message: 'Crisis BP reading: 190/110',
      is_resolved: false,
      created_at: '2026-06-23T10:00:00Z',
    },
    {
      id: 2,
      patient_name: 'Jane Smith',
      severity: 'HIGH',
      message: 'Stage 2 reading: 145/95',
      is_resolved: false,
      created_at: '2026-06-22T10:00:00Z',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    renderWithContext(<AlertsList />);
    expect(screen.getByText(/Loading alerts/i)).toBeInTheDocument();
  });

  it('renders alerts list when data is available', async () => {
    api.get.mockResolvedValue({ data: { results: mockAlerts } });
    renderWithContext(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('CRITICAL')).toBeInTheDocument();
      expect(screen.getByText('HIGH')).toBeInTheDocument();
    });
  });

  it('shows "No alerts" message when list is empty', async () => {
    api.get.mockResolvedValue({ data: { results: [] } });
    renderWithContext(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText(/No unresolved alerts/i)).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    api.get.mockRejectedValue(new Error('Network error'));
    renderWithContext(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText(/No unresolved alerts/i)).toBeInTheDocument();
    });
  });

  it('calls resolve alert when resolve button is clicked', async () => {
    api.get.mockResolvedValue({ data: { results: mockAlerts } });
    api.patch.mockResolvedValue({ data: {} });
    
    renderWithContext(<AlertsList />);

    await waitFor(() => {
      const resolveButtons = screen.getAllByText(/Resolve/i);
      fireEvent.click(resolveButtons[0]);
    });

    expect(api.patch).toHaveBeenCalledWith('/alerts/1/', { is_resolved: true });
  });
});