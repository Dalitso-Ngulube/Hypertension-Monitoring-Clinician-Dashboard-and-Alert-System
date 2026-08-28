import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Patients from '../Patients';
import api from '../../api/axiosConfig';
import { AuthContext } from '../../context/AuthContext';

jest.mock('../../api/axiosConfig');

const mockUser = {
  id: 1,
  username: 'clinician1',
  role: 'clinician',
};

const mockPatients = [
  { id: 1, first_name: 'John', last_name: 'Doe', age: 45, phone_number: '555-123-4567' },
  { id: 2, first_name: 'Jane', last_name: 'Smith', age: 52, phone_number: '555-987-6543' },
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

describe('Patients', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    renderWithContext(<Patients />);
    expect(document.querySelector('.spinner-border')).toBeInTheDocument();
  });

  it('renders patient list when data is available', async () => {
    api.get.mockResolvedValue({ data: { results: mockPatients } });
    renderWithContext(<Patients />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('45')).toBeInTheDocument();
      expect(screen.getByText('52')).toBeInTheDocument();
    });
  });

  it('filters patients by search term', async () => {
    api.get.mockResolvedValue({ data: { results: mockPatients } });
    renderWithContext(<Patients />);

    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText(/Search patients/i);
      fireEvent.change(searchInput, { target: { value: 'John' } });
    });

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
  });

  it('shows "No patients" message when list is empty', async () => {
    api.get.mockResolvedValue({ data: { results: [] } });
    renderWithContext(<Patients />);

    await waitFor(() => {
      expect(screen.getByText(/No Patients/i)).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    api.get.mockRejectedValue(new Error('Network error'));
    renderWithContext(<Patients />);

    await waitFor(() => {
      expect(screen.getByText(/No Patients/i)).toBeInTheDocument();
    });
  });

  it('opens Add Patient modal when Add button is clicked', async () => {
    api.get.mockResolvedValue({ data: { results: mockPatients } });
    renderWithContext(<Patients />);

    const addButton = screen.getAllByRole('button', { name: /Add Patient/i })[0];
    fireEvent.click(addButton);

    const modalTitle = await screen.findByText(/Add New Patient/i, {}, { timeout: 3000 });
    expect(modalTitle).toBeInTheDocument();
  });
});