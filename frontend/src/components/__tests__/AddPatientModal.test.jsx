import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AddPatientModal from '../AddPatientModal';
import api from '../../api/axiosConfig';

jest.mock('../../api/axiosConfig');

describe('AddPatientModal', () => {
  const mockOnPatientAdded = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const getInputByName = (name) => {
    const inputs = [
      ...screen.getAllByRole('textbox'),
      ...screen.getAllByRole('spinbutton'),
    ];
    return inputs.find(input => input.getAttribute('name') === name);
  };

  const getSelectByName = (name) => {
    return screen.getAllByRole('combobox').find(select => select.getAttribute('name') === name);
  };

  const openModal = () => {
    render(<AddPatientModal onPatientAdded={mockOnPatientAdded} />);
    fireEvent.click(screen.getAllByText('Add Patient')[0]);
  };

  it('renders the modal with form fields', () => {
    openModal();
    expect(screen.getByText('Add New Patient')).toBeInTheDocument();
    expect(getInputByName('first_name')).toBeInTheDocument();
    expect(getInputByName('last_name')).toBeInTheDocument();
    expect(getInputByName('age')).toBeInTheDocument();
    expect(getSelectByName('gender')).toBeInTheDocument();
    expect(getInputByName('phone_number')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getAllByText('Add Patient')[1]).toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    api.post.mockResolvedValue({ data: { id: 1 } });
    openModal();

    fireEvent.change(getInputByName('first_name'), { target: { value: 'John' } });
    fireEvent.change(getInputByName('last_name'), { target: { value: 'Doe' } });
    fireEvent.change(getInputByName('age'), { target: { value: '45' } });
    fireEvent.change(getSelectByName('gender'), { target: { value: 'M' } });
    fireEvent.change(getInputByName('phone_number'), { target: { value: '555-123-4567' } });

    fireEvent.click(screen.getAllByText('Add Patient')[1]);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/patients/', expect.objectContaining({
        first_name: 'John',
        last_name: 'Doe',
        age: 45,
        gender: 'M',
        phone_number: '555-123-4567',
      }));
      expect(mockOnPatientAdded).toHaveBeenCalledWith({ id: 1 });
    });
  });

  it('shows validation errors for missing required fields', async () => {
    openModal();
    fireEvent.click(screen.getAllByText('Add Patient')[1]);

    await waitFor(() => {
      expect(getInputByName('first_name')).toHaveAttribute('required');
      expect(getInputByName('last_name')).toHaveAttribute('required');
      expect(getInputByName('age')).toHaveAttribute('required');
    });
  });

  it('handles API error gracefully', async () => {
    api.post.mockRejectedValue({ response: { data: { error: 'Server error' } } });
    openModal();

    fireEvent.change(getInputByName('first_name'), { target: { value: 'John' } });
    fireEvent.change(getInputByName('last_name'), { target: { value: 'Doe' } });
    fireEvent.change(getInputByName('age'), { target: { value: '45' } });
    fireEvent.click(screen.getAllByText('Add Patient')[1]);

    await waitFor(() => {
      expect(screen.getByText(/Failed to add patient/i)).toBeInTheDocument();
    });
  });

  it('calls onPatientAdded with new patient data on success', async () => {
    const newPatient = { id: 1, first_name: 'John', last_name: 'Doe' };
    api.post.mockResolvedValue({ data: newPatient });
    openModal();

    fireEvent.change(getInputByName('first_name'), { target: { value: 'John' } });
    fireEvent.change(getInputByName('last_name'), { target: { value: 'Doe' } });
    fireEvent.change(getInputByName('age'), { target: { value: '45' } });
    fireEvent.click(screen.getAllByText('Add Patient')[1]);

    await waitFor(() => {
      expect(mockOnPatientAdded).toHaveBeenCalledWith(newPatient);
    });
  });

  it('closes modal when clicking close button', () => {
    openModal();
    const closeBtn = document.querySelector('.btn-close');
    if (closeBtn) {
      fireEvent.click(closeBtn);
      expect(screen.queryByText('Add New Patient')).not.toBeInTheDocument();
    }
  });
});