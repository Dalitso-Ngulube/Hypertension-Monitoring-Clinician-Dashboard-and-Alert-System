import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import BPHistoryTable from '../BPHistoryTable';
import api from '../../api/axiosConfig';

jest.mock('../../api/axiosConfig');

describe('BPHistoryTable', () => {
  const mockReadings = [
    {
      id: 1,
      systolic: 140,
      diastolic: 90,
      pulse_rate: 72,
      recorded_at: '2026-06-23T10:00:00Z',
      risk_category: 'STAGE_2',
      source: 'MANUAL',
    },
    {
      id: 2,
      systolic: 120,
      diastolic: 80,
      pulse_rate: 68,
      recorded_at: '2026-06-22T10:00:00Z',
      risk_category: 'NORMAL',
      source: 'API',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading state while fetching data', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    render(<BPHistoryTable patientId={1} />);
    expect(screen.getByText(/Loading BP history/i)).toBeInTheDocument();
  });

  it('renders averages and table when data is available', async () => {
    api.get.mockResolvedValue({ data: { results: mockReadings } });
    render(<BPHistoryTable patientId={1} />);

    await waitFor(() => {
      expect(screen.getByText('Avg Systolic')).toBeInTheDocument();
      expect(screen.getByText('140')).toBeInTheDocument();
      expect(screen.getByText('Avg Diastolic')).toBeInTheDocument();
      expect(screen.getByText('90')).toBeInTheDocument();
      expect(screen.getByText('STAGE_2')).toBeInTheDocument();
      expect(screen.getByText('NORMAL')).toBeInTheDocument();
    });
  });

  it('shows "No readings" message when empty', async () => {
    api.get.mockResolvedValue({ data: { results: [] } });
    render(<BPHistoryTable patientId={1} />);

    await waitFor(() => {
      expect(screen.getByText(/No BP readings recorded/i)).toBeInTheDocument();
    });
  });

  it('fetches the logged-in patient readings when patientId is missing', async () => {
    api.get.mockResolvedValue({ data: { results: [] } });
    render(<BPHistoryTable patientId={null} />);

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/bp_readings/');
      expect(screen.getByText(/No BP readings recorded/i)).toBeInTheDocument();
    });
  });
});