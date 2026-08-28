import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AddReadingModal from '../AddReadingModal';
import api from '../../api/axiosConfig';

jest.mock('../../api/axiosConfig');

describe('AddReadingModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const openModal = async () => {
    render(<AddReadingModal onClose={mockOnClose} onSuccess={mockOnSuccess} />);
    const openButton = screen.getByRole('button', { name: /Add Reading/i });
    fireEvent.click(openButton);
    await screen.findByText('Add Blood Pressure Reading');
  };

  it('renders the modal with form fields', async () => {
    await openModal();
    expect(screen.getByText('Add Blood Pressure Reading')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g., 120')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g., 80')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g., 72')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: /Add Reading/i })).toHaveLength(2);
  });

  it('submits form with valid data', async () => {
    api.post.mockResolvedValue({ data: {} });
    await openModal();

    const systolicInput = screen.getByPlaceholderText('e.g., 120');
    const diastolicInput = screen.getByPlaceholderText('e.g., 80');
    const pulseInput = screen.getByPlaceholderText('e.g., 72');

    fireEvent.change(systolicInput, { target: { value: '140' } });
    fireEvent.change(diastolicInput, { target: { value: '90' } });
    fireEvent.change(pulseInput, { target: { value: '72' } });

    const form = document.querySelector('form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/bp_readings/', {
        systolic: 140,
        diastolic: 90,
        pulse_rate: 72,
      });
      expect(mockOnSuccess).toHaveBeenCalled();
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it('handles API error gracefully', async () => {
    api.post.mockRejectedValue({ response: { data: { error: 'Server error' } } });
    await openModal();

    const systolicInput = screen.getByPlaceholderText('e.g., 120');
    const diastolicInput = screen.getByPlaceholderText('e.g., 80');

    fireEvent.change(systolicInput, { target: { value: '140' } });
    fireEvent.change(diastolicInput, { target: { value: '90' } });
    const form = document.querySelector('form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText(/Failed to add reading/i)).toBeInTheDocument();
    });
  });

  it('calls onClose when Cancel is clicked', async () => {
    await openModal();
    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    fireEvent.click(cancelButton);
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('closes modal when clicking close button', async () => {
    await openModal();
    const closeBtn = document.querySelector('.btn-close');
    if (closeBtn) {
      fireEvent.click(closeBtn);
      expect(screen.queryByText('Add Blood Pressure Reading')).not.toBeInTheDocument();
    }
  });
});