import React from 'react';
import { render, screen } from '@testing-library/react';
import PatientInfoCard from '../PatientInfoCard';

describe('PatientInfoCard', () => {
  const mockPatient = {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    age: 45,
    gender: 'M',
    phone_number: '555-123-4567',
    email: 'john@example.com',
  };

  const mockLatestReading = {
    systolic: 140,
    diastolic: 90,
    pulse_rate: 72,
    recorded_at: '2026-06-23T10:00:00Z',
    risk_category: 'STAGE_2',
  };

  it('renders patient information correctly', () => {
    render(<PatientInfoCard patient={mockPatient} latestReading={mockLatestReading} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    
    const ageElements = screen.getAllByText((content, element) => 
      element.textContent.includes('Age: 45')
    );
    expect(ageElements.length).toBeGreaterThan(0);
    expect(ageElements[0]).toBeInTheDocument();
    expect(screen.getByText(/ID: 0001/)).toBeInTheDocument();
  });

  it('displays latest reading when available', () => {
    render(<PatientInfoCard patient={mockPatient} latestReading={mockLatestReading} />);
    expect(screen.getByText(/140\/90/)).toBeInTheDocument();
    expect(screen.getByText('72')).toBeInTheDocument();
    expect(screen.getByText('STAGE_2')).toBeInTheDocument();
  });

  it('shows "No readings" when latest reading is null', () => {
    render(<PatientInfoCard patient={mockPatient} latestReading={null} />);
    expect(screen.getByText(/No readings available for this patient./i)).toBeInTheDocument();
  });

  it('handles missing patient data gracefully', () => {
    render(<PatientInfoCard patient={null} latestReading={null} />);
    expect(screen.getByText(/Select a patient to view their profile/i)).toBeInTheDocument();
  });

  it('displays patient initials as avatar', () => {
    render(<PatientInfoCard patient={mockPatient} latestReading={mockLatestReading} />);
    expect(screen.getByText('JD')).toBeInTheDocument();
  });
});