import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PatientSelector from '../PatientSelector';
import api from '../../api/axiosConfig';

jest.mock('../../api/axiosConfig');

describe('PatientSelector', () => {
  const mockPatients = [
    { id: 1, first_name: 'John', last_name: 'Doe', age: 45 },
    { id: 2, first_name: 'Jane', last_name: 'Smith', age: 52 },
  ];

  const mockOnSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    render(<PatientSelector onSelectPatient={mockOnSelect} />);
    expect(screen.getByText(/Loading patients/i)).toBeInTheDocument();
  });

  it('renders patient list when API responds', async () => {
    api.get.mockResolvedValue({ data: { results: mockPatients } });
    render(<PatientSelector onSelectPatient={mockOnSelect} />);

    await waitFor(() => {
      const options = screen.getAllByRole('option');
      expect(options).toHaveLength(3);
      expect(options[1].textContent).toContain('John');
      expect(options[1].textContent).toContain('Doe');
      expect(options[1].textContent).toContain('Age: 45');
      expect(options[2].textContent).toContain('Jane');
      expect(options[2].textContent).toContain('Smith');
      expect(options[2].textContent).toContain('Age: 52');
    });
  });

  it('handles API error gracefully', async () => {
    api.get.mockRejectedValue(new Error('Network error'));
    render(<PatientSelector onSelectPatient={mockOnSelect} />);

    await waitFor(() => {
      const options = screen.getAllByRole('option');
      expect(options).toHaveLength(1);
      expect(options[0]).toHaveTextContent('-- Choose a patient --');
    });
  });

  it('calls onSelectPatient when a patient is selected', async () => {
    api.get.mockResolvedValue({ data: { results: mockPatients } });
    render(<PatientSelector onSelectPatient={mockOnSelect} />);

    await waitFor(() => {
      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: '1' } });
    });

    expect(mockOnSelect).toHaveBeenCalledWith(1);
  });

  it('shows "No patients found" when list is empty', async () => {
    api.get.mockResolvedValue({ data: { results: [] } });
    render(<PatientSelector onSelectPatient={mockOnSelect} />);

    await waitFor(() => {
      const options = screen.getAllByRole('option');
      expect(options).toHaveLength(1);
      expect(options[0]).toHaveTextContent(/-- Choose a patient --/i);
    });
  });
});