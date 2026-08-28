import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import api from '../api/axiosConfig';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const TrendChart = ({ patientId, days }) => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // If no patient is selected, clear the chart
    if (!patientId) {
      setChartData(null);
      setLoading(false);
      return;
    }

    const fetchReadings = async () => {
      setLoading(true);
      try {
        // Fetch readings for the specific patient
        const response = await api.get(`/bp_readings/?patient=${patientId}`);
        let readings = response.data.results || [];

        // Filter by days (default: 30)
        if (days && days > 0) {
          const cutoff = new Date();
          cutoff.setDate(cutoff.getDate() - days);
          readings = readings.filter((r) => new Date(r.recorded_at) >= cutoff);
        }

        // Sort chronologically
        readings.sort((a, b) => new Date(a.recorded_at) - new Date(b.recorded_at));

        if (readings.length === 0) {
          setChartData(null);
          setLoading(false);
          return;
        }

        const labels = readings.map((r) => new Date(r.recorded_at).toLocaleDateString());
        const systolic = readings.map((r) => r.systolic);
        const diastolic = readings.map((r) => r.diastolic);

        setChartData({
          labels,
          datasets: [
            {
              label: 'Systolic',
              data: systolic,
              borderColor: '#e53e3e',
              backgroundColor: 'rgba(229,62,62,0.1)',
              tension: 0.2,
              fill: true,
              pointRadius: 4,
              pointBackgroundColor: '#e53e3e',
            },
            {
              label: 'Diastolic',
              data: diastolic,
              borderColor: '#3182ce',
              backgroundColor: 'rgba(49,130,206,0.1)',
              tension: 0.2,
              fill: true,
              pointRadius: 4,
              pointBackgroundColor: '#3182ce',
            },
          ],
        });
      } catch (error) {
        console.error('Error fetching readings:', error);
        setChartData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchReadings();
  }, [patientId, days]);

  // Render states
  if (!patientId) {
    return <div className="text-center text-muted py-4">Select a patient to view trends</div>;
  }

  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="spinner-border spinner-border-sm text-primary" />
      </div>
    );
  }

  if (!chartData) {
    return <div className="text-center text-warning py-4">No readings found for this period.</div>;
  }

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top', labels: { font: { size: 10 } } },
      title: {
        display: true,
        text: `Blood Pressure Readings (Last ${days} Days)`,
        font: { size: 12 },
      },
    },
    scales: {
      y: {
        title: { display: true, text: 'mmHg' },
        min: 50,
        max: 220,
      },
    },
  };

  return <Line data={chartData} options={options} />;
};

export default TrendChart;