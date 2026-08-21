import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import api from '../api/axiosConfig';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const TrendChart = ({ patientId, days }) => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!patientId) return;
    const fetchTrend = async () => {
      setLoading(true);
      try {
        const response = await api.get(`/analytics/trends/${patientId}/?days=${days}`);
        const data = response.data;
        if (data.length === 0) { setChartData(null); setLoading(false); return; }
        const labels = data.map((item) => new Date(item.date).toLocaleDateString());
        const systolic = data.map((item) => Math.round(item.avg_systolic));
        const diastolic = data.map((item) => Math.round(item.avg_diastolic));
        setChartData({
          labels,
          datasets: [
            { label: 'Systolic (mmHg)', data: systolic, borderColor: '#e53e3e', backgroundColor: 'rgba(229,62,62,0.08)', tension: 0.3, fill: true, pointRadius: 3 },
            { label: 'Diastolic (mmHg)', data: diastolic, borderColor: '#3182ce', backgroundColor: 'rgba(49,130,206,0.08)', tension: 0.3, fill: true, pointRadius: 3 },
          ],
        });
      } catch (error) { console.error(error); } finally { setLoading(false); }
    };
    fetchTrend();
  }, [patientId, days]);

  if (!patientId) return <div className="text-center text-muted py-4">Select a patient to view trends</div>;
  if (loading) return <div className="text-center py-4"><div className="spinner-border spinner-border-sm text-primary" /></div>;
  if (!chartData) return <div className="text-center text-warning py-4">No readings found for this period.</div>;

  const options = {
    responsive: true,
    plugins: { legend: { position: 'top', labels: { font: { size: 10 } } }, title: { display: true, text: `Blood Pressure Trend (Last ${days} Days)`, font: { size: 12 } } },
    scales: { y: { title: { display: true, text: 'mmHg' }, min: 50, max: 220 } },
  };
  return <Line data={chartData} options={options} />;
};

export default TrendChart;