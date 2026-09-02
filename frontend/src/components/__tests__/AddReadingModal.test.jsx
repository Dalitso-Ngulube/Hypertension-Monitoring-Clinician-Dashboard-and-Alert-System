import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AddReadingModal from '../AddReadingModal';
import api from '../../api/axiosConfig';

jest.mock('../../api/axiosConfig', () => ({
  post: jest.fn(),
}));

describe('AddReadingModal', () => {
  const mockOnSuccess = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('submits form with valid data', async () => {
    api.post.mockResolvedValueOnce({ data: { id: 1 } });
    render(<AddReadingModal patientId={1} patientName="John Doe" onReadingAdded={mockOnSuccess} onClose={mockOnClose} />);

    const openButton = screen.getByRole('button', { name: /Add Reading/i });
    fireEvent.click(openButton);

    const modalTitle = await screen.findByText(/Add Reading for John Doe/i);
    expect(modalTitle).toBeInTheDocument();

    const systolicInput = screen.getByPlaceholderText('e.g., 120');
    const diastolicInput = screen.getByPlaceholderText('e.g., 80');
    const pulseInput = screen.getByPlaceholderText('e.g., 72');

    fireEvent.change(systolicInput, { target: { value: '120' } });
    fireEvent.change(diastolicInput, { target: { value: '80' } });
    fireEvent.change(pulseInput, { target: { value: '72' } });

    const submitButton = screen.getByRole('button', { name: /Save/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it('calls onClose when Cancel is clicked', async () => {
    render(<AddReadingModal patientId={1} patientName="John Doe" onReadingAdded={mockOnSuccess} onClose={mockOnClose} />);
    const openButton = screen.getByRole('button', { name: /Add Reading/i });
    fireEvent.click(openButton);

    await screen.findByText(/Add Reading for John Doe/i);
    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    fireEvent.click(cancelButton);
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('calls onClose when clicking close button', async () => {
    render(<AddReadingModal patientId={1} patientName="John Doe" onReadingAdded={mockOnSuccess} onClose={mockOnClose} />);
    const openButton = screen.getByRole('button', { name: /Add Reading/i });
    fireEvent.click(openButton);

    await screen.findByText(/Add Reading for John Doe/i);
    const closeButton = screen.getByRole('button', { name: /Close/i });
    fireEvent.click(closeButton);
    expect(mockOnClose).toHaveBeenCalled();
  });
});