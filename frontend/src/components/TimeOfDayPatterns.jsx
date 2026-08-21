import React, { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import { Clock, Sun, Cloud, Moon } from 'lucide-react';

const TimeOfDayPatterns = ({ patientId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(`/analytics/patient/${patientId}/time-patterns/`);
        setData(response.data);
      } catch (error) { console.error(error); } finally { setLoading(false); }
    };
    if (patientId) fetchData();
  }, [patientId]);

  if (loading) return <div className="text-center py-3 text-muted small">Loading time patterns...</div>;
  if (!data) return null;

  const slots = [
    { key: 'morning', label: 'Morning', icon: Sun, time: '6 AM – 12 PM' },
    { key: 'afternoon', label: 'Afternoon', icon: Cloud, time: '12 PM – 6 PM' },
    { key: 'evening', label: 'Evening', icon: Moon, time: '6 PM – 12 AM' },
    { key: 'night', label: 'Night', icon: Moon, time: '12 AM – 6 AM' },
  ];

  const hasData = slots.some(slot => data[slot.key]?.count > 0);
  if (!hasData) return <div className="card card-clinical"><div className="card-body text-center py-3 text-muted"><Clock size={24} className="mb-2" /><p className="small mb-0">No time-of-day data available.</p></div></div>;

  return (
    <div className="card card-clinical">
      <div className="card-header"><Clock size={16} className="me-2" /> BP by Time of Day</div>
      <div className="card-body">
        <div className="row g-2">
          {slots.map(slot => {
            const slotData = data[slot.key];
            const Icon = slot.icon;
            return (
              <div key={slot.key} className="col-6 col-md-3">
                <div className={`p-2 rounded-3 text-center ${slotData?.count > 0 ? 'bg-white border' : 'bg-light opacity-50'}`}>
                  <Icon size={16} className="text-muted" />
                  <div className="small fw-semibold">{slot.label}</div>
                  {slotData?.count > 0 ? (
                    <>
                      <div className="fw-bold">{slotData.avg_systolic !== null ? `${slotData.avg_systolic}/${slotData.avg_diastolic}` : '—'}</div>
                      <div className="small text-muted">{slotData.count} readings</div>
                    </>
                  ) : <div className="small text-muted">No data</div>}
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-2 pt-2 border-top small text-muted">High morning readings may indicate masked hypertension.</div>
      </div>
    </div>
  );
};

export default TimeOfDayPatterns;