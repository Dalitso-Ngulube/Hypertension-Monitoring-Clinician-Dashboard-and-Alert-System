import React, { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import { Calendar, Clock, Activity, Droplet, Heart, TrendingDown, TrendingUp, Minus } from 'lucide-react';

const BPHistoryTable = ({ patientId }) => {
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [averages, setAverages] = useState({ systolic: 0, diastolic: 0, pulse: 0, count: 0 });

  useEffect(() => {
    const fetchReadings = async () => {
      if (!patientId) {
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const response = await api.get(`/bp_readings/?patient=${patientId}`);
        const data = response.data.results || [];

        // Sort: newest first
        const sorted = data.sort((a, b) => new Date(b.recorded_at) - new Date(a.recorded_at));
        setReadings(sorted);

        // Calculate averages
        if (sorted.length > 0) {
          const totalSystolic = sorted.reduce((sum, r) => sum + r.systolic, 0);
          const totalDiastolic = sorted.reduce((sum, r) => sum + r.diastolic, 0);
          const totalPulse = sorted.reduce((sum, r) => sum + (r.pulse_rate || 0), 0);
          const pulseCount = sorted.filter(r => r.pulse_rate).length;

          setAverages({
            systolic: Math.round(totalSystolic / sorted.length),
            diastolic: Math.round(totalDiastolic / sorted.length),
            pulse: pulseCount > 0 ? Math.round(totalPulse / pulseCount) : 0,
            count: sorted.length,
          });
        } else {
          setAverages({ systolic: 0, diastolic: 0, pulse: 0, count: 0 });
        }
      } catch (error) {
        console.error('Error fetching BP history:', error);
        setReadings([]);
        setAverages({ systolic: 0, diastolic: 0, pulse: 0, count: 0 });
      } finally {
        setLoading(false);
      }
    };

    fetchReadings();
  }, [patientId]);

  const getRiskBadge = (category) => {
    const colors = {
      CRISIS: 'bg-red-500 text-white',
      STAGE_2: 'bg-orange-500 text-white',
      STAGE_1: 'bg-yellow-500 text-white',
      ELEVATED: 'bg-blue-400 text-white',
      NORMAL: 'bg-green-500 text-white',
    };
    return colors[category] || 'bg-gray-400 text-white';
  };

  const getTrendIcon = (value, type) => {
    if (readings.length < 2) return <Minus size={14} className="text-gray-400" />;
    const latest = readings[0][type];
    const previous = readings[1][type];
    if (latest > previous) return <TrendingUp size={14} className="text-red-500" />;
    if (latest < previous) return <TrendingDown size={14} className="text-green-500" />;
    return <Minus size={14} className="text-gray-400" />;
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="spinner-border spinner-border-sm text-primary" />
        <p className="text-muted mt-2">Loading BP history...</p>
      </div>
    );
  }

  if (readings.length === 0) {
    return (
      <div className="card-soft text-center py-8">
        <Activity size={40} className="mx-auto text-gray-300 mb-2" />
        <h5 className="text-gray-500">No BP readings recorded</h5>
        <p className="text-sm text-gray-400">Add a reading to start tracking.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Averages Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="stat-card bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
          <div className="stat-icon bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400">
            <Droplet size={16} />
          </div>
          <div>
            <div className="stat-label">Avg Systolic</div>
            <div className="stat-number">{averages.systolic} <span className="text-xs font-normal text-gray-400">mmHg</span></div>
          </div>
        </div>
        <div className="stat-card bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
          <div className="stat-icon bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400">
            <Droplet size={16} />
          </div>
          <div>
            <div className="stat-label">Avg Diastolic</div>
            <div className="stat-number">{averages.diastolic} <span className="text-xs font-normal text-gray-400">mmHg</span></div>
          </div>
        </div>
        <div className="stat-card bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
          <div className="stat-icon bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400">
            <Heart size={16} />
          </div>
          <div>
            <div className="stat-label">Avg Pulse</div>
            <div className="stat-number">{averages.pulse} <span className="text-xs font-normal text-gray-400">bpm</span></div>
          </div>
        </div>
      </div>

      <p className="text-sm text-gray-500 dark:text-gray-400">
        {averages.count} reading{averages.count !== 1 ? 's' : ''} total
      </p>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Date / Time</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Systolic</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Diastolic</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Pulse</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Risk</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Source</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
            {readings.map((reading) => (
              <tr key={reading.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                <td className="px-4 py-3 whitespace-nowrap text-slate-700 dark:text-slate-300">
                  <div className="flex items-center gap-1">
                    <Calendar size={12} className="text-gray-400" />
                    {new Date(reading.recorded_at).toLocaleDateString()}
                    <Clock size={12} className="text-gray-400 ml-2" />
                    {new Date(reading.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap font-medium text-slate-800 dark:text-white">
                  {reading.systolic} <span className="text-xs text-gray-400">mmHg</span>
                  {readings.length > 1 && reading.id === readings[0].id && (
                    <span className="ml-1 inline-block">{getTrendIcon(reading, 'systolic')}</span>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap font-medium text-slate-800 dark:text-white">
                  {reading.diastolic} <span className="text-xs text-gray-400">mmHg</span>
                  {readings.length > 1 && reading.id === readings[0].id && (
                    <span className="ml-1 inline-block">{getTrendIcon(reading, 'diastolic')}</span>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-slate-700 dark:text-slate-300">
                  {reading.pulse_rate || '—'}
                  {reading.pulse_rate && <span className="text-xs text-gray-400"> bpm</span>}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${getRiskBadge(reading.risk_category)}`}>
                    {reading.risk_category || 'UNKNOWN'}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-xs text-gray-500">
                  {reading.source || 'MANUAL'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BPHistoryTable;