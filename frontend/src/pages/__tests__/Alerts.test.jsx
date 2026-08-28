import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Alerts from '../Alerts';
import api from '../../api/axiosConfig';
import { AuthContext } from '../../context/AuthContext';

jest.mock('../../api/axiosConfig');

const mockUser = {
  id: 1,
  username: 'clinician1',
  role: 'clinician',
};

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

const renderWithContext = (component) => {
  return render(
    <AuthContext.Provider value={{ user: mockUser, isAuthenticated: true }}>
      {component}
    </AuthContext.Provider>
  );
};

describe('Alerts', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    renderWithContext(<Alerts />);
    expect(document.querySelector('.spinner-border')).toBeInTheDocument();
  });

  it('renders alerts with stats summary', async () => {
    api.get.mockResolvedValue({ data: { results: mockAlerts } });
    renderWithContext(<Alerts />);

    await waitFor(() => {
      expect(screen.getByText('Alerts')).toBeInTheDocument();
      // Use more specific selector to avoid duplicate text
      const criticalStat = screen.getAllByText('Critical')[0];
      expect(criticalStat).toBeInTheDocument();
      const highStat = screen.getAllByText('High')[0];
      expect(highStat).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('filters alerts by search term', async () => {
    api.get.mockResolvedValue({ data: { results: mockAlerts } });
    renderWithContext(<Alerts />);

    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText(/Search alerts/i);
      fireEvent.change(searchInput, { target: { value: 'John' } });
    });

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
  });

  it('filters alerts by severity', async () => {
    api.get.mockResolvedValue({ data: { results: mockAlerts } });
    renderWithContext(<Alerts />);

    await waitFor(() => {
      const filterSelect = screen.getByRole('combobox');
      fireEvent.change(filterSelect, { target: { value: 'CRITICAL' } });
    });

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
    });
  });

  it('shows "No alerts" message when list is empty', async () => {
    api.get.mockResolvedValue({ data: { results: [] } });
    renderWithContext(<Alerts />);

    await waitFor(() => {
      expect(screen.getByText(/No alerts/i)).toBeInTheDocument();
    });
  });
});