import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import PatientDetails from '../PatientDetails';
import api from '../../api/axiosConfig';
import { AuthContext } from '../../context/AuthContext';

jest.mock('../../api/axiosConfig');

const mockUser = {
  id: 1,
  username: 'clinician1',
  role: 'clinician',
};

const mockPatient = {
  id: 1,
  first_name: 'John',
  last_name: 'Doe',
  age: 45,
  gender: 'M',
  phone_number: '555-123-4567',
  email: 'john@example.com',
  address: '123 Main St',
};

const renderWithContext = (component) => {
  return render(
    <MemoryRouter initialEntries={['/patients/1']}>
      <AuthContext.Provider value={{ user: mockUser, isAuthenticated: true }}>
        <Routes>
          <Route path="/patients/:id" element={component} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>
  );
};

describe('PatientDetails', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    renderWithContext(<PatientDetails />);
    expect(screen.getByText(/Loading patient details/i)).toBeInTheDocument();
  });

  it('renders patient information and sections', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockPatient })
      .mockResolvedValueOnce({ data: { results: [] } })
      .mockResolvedValueOnce({ data: {} });

    renderWithContext(<PatientDetails />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const idElements = screen.getAllByText((content, element) =>
      element.textContent.includes('Patient ID: 0001')
    );
    expect(idElements.length).toBeGreaterThan(0);

    const ageElements = screen.getAllByText((content, element) =>
      element.textContent.includes('Age: 45')
    );
    expect(ageElements.length).toBeGreaterThan(0);

    expect(screen.getByText('BP History & Averages')).toBeInTheDocument();
  });

  it('toggles BP History visibility', async () => {
    api.get
      .mockResolvedValueOnce({ data: mockPatient })
      .mockResolvedValueOnce({ data: { results: [] } })
      .mockResolvedValueOnce({ data: {} });

    renderWithContext(<PatientDetails />);

    await waitFor(() => {
      const toggleButton = screen.getByText('Hide History');
      fireEvent.click(toggleButton);
    });

    expect(screen.queryByText('No BP readings recorded')).not.toBeInTheDocument();
  });

  it('shows "Patient not found" for invalid ID', async () => {
    api.get.mockRejectedValue({ response: { status: 404 } });
    renderWithContext(<PatientDetails />);

    await waitFor(() => {
      expect(screen.getByText(/Patient not found/i)).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    api.get.mockRejectedValue(new Error('Network error'));
    renderWithContext(<PatientDetails />);

    await waitFor(() => {
      expect(screen.getByText(/Patient not found/i)).toBeInTheDocument();
    });
  });
});