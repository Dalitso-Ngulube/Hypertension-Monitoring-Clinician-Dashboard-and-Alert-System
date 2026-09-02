import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import Patients from '../Patients';
import api from '../../api/axiosConfig';

jest.mock('../../api/axiosConfig', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
}));

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const renderWithContext = (component, user) => {
  return render(
    <BrowserRouter>
      <AuthContext.Provider value={{ user, token: 'mock-token' }}>
        {component}
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('Patients', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockPatients = [
    { id: 1, first_name: 'John', last_name: 'Doe', age: 45, gender: 'M', phone_number: '555-123-4567', user: { email: 'john@example.com' } },
    { id: 2, first_name: 'Jane', last_name: 'Smith', age: 52, gender: 'F', phone_number: '555-987-6543', user: { email: 'jane@example.com' } },
  ];

  it('renders patient list', async () => {
    api.get.mockResolvedValueOnce({ data: { results: mockPatients } });
    renderWithContext(<Patients />, { role: 'clinician' });
    expect(await screen.findByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('opens Add Patient modal when Add button is clicked', async () => {
    api.get.mockResolvedValueOnce({ data: { results: mockPatients } });
    renderWithContext(<Patients />, { role: 'clinician' });

    await screen.findByText('John Doe');

    const outerAddButton = screen.getByRole('button', { name: /Add Patient/i });
    fireEvent.click(outerAddButton);

    const innerAddButton = screen.getAllByRole('button', { name: /Add Patient/i })[1];
    fireEvent.click(innerAddButton);

    const modalTitle = await screen.findByText(/Add New Patient/i);
    expect(modalTitle).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    renderWithContext(<Patients />, { role: 'clinician' });
    expect(screen.getByText(/Loading patients/i)).toBeInTheDocument();
  });

  it('shows error message on API failure', async () => {
    api.get.mockRejectedValueOnce({ response: { data: { detail: 'Server error' } } });
    renderWithContext(<Patients />, { role: 'clinician' });
    const errorMessage = await screen.findByText(/Failed to load patients/i);
    expect(errorMessage).toBeInTheDocument();
  });

  it('shows patient details when Details button is clicked', async () => {
    api.get.mockResolvedValueOnce({ data: { results: mockPatients } });
    renderWithContext(<Patients />, { role: 'clinician' });

    await screen.findByText('John Doe');

    const detailsButton = screen.getAllByRole('button', { name: /Details/i })[0];
    fireEvent.click(detailsButton);

    expect(await screen.findByText(/Back to Patients/i)).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('filters patients by search term', async () => {
    api.get.mockResolvedValueOnce({ data: { results: mockPatients } });
    renderWithContext(<Patients />, { role: 'clinician' });
    await screen.findByText('John Doe');
    const searchInput = screen.getByPlaceholderText(/Search patients/i);
    fireEvent.change(searchInput, { target: { value: 'Jane' } });
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
  });
});