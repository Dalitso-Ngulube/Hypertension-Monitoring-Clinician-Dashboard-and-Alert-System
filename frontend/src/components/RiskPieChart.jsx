import React, { useState, useEffect } from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import api from '../api/axiosConfig';

ChartJS.register(ArcElement, Tooltip, Legend);

const RISK_COLORS = { CRISIS: '#c53030', STAGE_2: '#e53e3e', STAGE_1: '#dd6b20', ELEVATED: '#ed8936', NORMAL: '#48bb78' };

const RiskPieChart = () => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDistribution = async () => {
      try {
        const response = await api.get('/analytics/risk-distribution/');
        const data = response.data;
        const labels = Object.keys(data);
        const values = Object.values(data);
        const colors = labels.map((label) => RISK_COLORS[label] || '#6c757d');
        setChartData({ labels, datasets: [{ data: values, backgroundColor: colors, borderColor: colors.map(() => '#fff'), borderWidth: 2 }] });
      } catch (error) { console.error(error); } finally { setLoading(false); }
    };
    fetchDistribution();
  }, []);

  if (loading) return <div className="text-center py-3"><div className="spinner-border spinner-border-sm text-primary" /></div>;
  if (!chartData || chartData.datasets[0].data.length === 0) return <div className="text-center text-muted py-3">No risk data available</div>;

  const options = { responsive: true, plugins: { legend: { position: 'bottom', labels: { font: { size: 10 } } } }, maintainAspectRatio: false };
  return <Pie data={chartData} options={options} style={{ height: '200px' }} />;
};

export default RiskPieChart;