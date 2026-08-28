import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import TrendChart from '../TrendChart';
import api from '../../api/axiosConfig';

jest.mock('../../api/axiosConfig');
jest.mock('react-chartjs-2', () => ({
  Line: () => <canvas data-testid="chart-canvas" />,
}));

describe('TrendChart', () => {
  const now = new Date();
  const mockReadings = [
    { id: 1, systolic: 140, diastolic: 90, recorded_at: new Date(now - 2 * 24 * 60 * 60 * 1000).toISOString() },
    { id: 2, systolic: 130, diastolic: 85, recorded_at: new Date(now - 1 * 24 * 60 * 60 * 1000).toISOString() },
    { id: 3, systolic: 120, diastolic: 80, recorded_at: new Date(now - 0.5 * 24 * 60 * 60 * 1000).toISOString() },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows "Select a patient" when no patient selected', () => {
    render(<TrendChart patientId={null} days={30} />);
    expect(screen.getByText(/Select a patient to view trends/i)).toBeInTheDocument();
  });

  it('shows loading state while fetching data', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    render(<TrendChart patientId={1} days={30} />);
    expect(document.querySelector('.spinner-border')).toBeInTheDocument();
  });

  it('renders chart when data is available', async () => {
    api.get.mockResolvedValue({ data: { results: mockReadings } });
    render(<TrendChart patientId={1} days={30} />);

    await waitFor(() => {
      const canvas = screen.getByTestId('chart-canvas');
      expect(canvas).toBeInTheDocument();
    });
  });

  it('shows "No readings" message when data is empty', async () => {
    api.get.mockResolvedValue({ data: { results: [] } });
    render(<TrendChart patientId={1} days={30} />);

    await waitFor(() => {
      expect(screen.getByText(/No readings found for this period/i)).toBeInTheDocument();
    });
  });

  it('handles API error', async () => {
    api.get.mockRejectedValue(new Error('Network error'));
    render(<TrendChart patientId={1} days={30} />);

    await waitFor(() => {
      expect(screen.getByText(/No readings found for this period/i)).toBeInTheDocument();
    });
  });

  it('filters readings by days', async () => {
    const fetchMock = api.get.mockResolvedValue({ data: { results: mockReadings } });
    render(<TrendChart patientId={1} days={7} />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith('/bp_readings/?patient=1');
    });
  });
});