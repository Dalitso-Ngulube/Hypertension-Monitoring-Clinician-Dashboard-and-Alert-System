import React, { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import { AlertCircle, Pill, Microscope, Heart, Activity, Loader } from 'lucide-react';

const ClinicalDecisionSupport = ({ patientId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCDS = async () => {
      try {
        const response = await api.get(`/analytics/cds/${patientId}/`);
        setData(response.data);
      } catch (err) { setError('Could not load CDS recommendations.'); } finally { setLoading(false); }
    };
    if (patientId) fetchCDS();
  }, [patientId]);

  if (loading) return <div className="text-center py-3"><div className="spinner-border spinner-border-sm text-primary" /></div>;
  if (error) return <div className="text-danger text-center py-3">{error}</div>;
  if (!data) return null;
  if (data.error) return <div className="text-warning text-center py-3">{data.error}</div>;

  const getStageBadge = (stage) => {
    const colors = {
      CRISIS: 'bg-danger bg-opacity-10 text-danger',
      STAGE_2: 'bg-danger bg-opacity-10 text-danger',
      STAGE_1: 'bg-warning bg-opacity-10 text-warning',
      ELEVATED: 'bg-info bg-opacity-10 text-info',
      NORMAL: 'bg-success bg-opacity-10 text-success',
    };
    return colors[stage] || 'bg-secondary bg-opacity-10 text-secondary';
  };

  return (
    <div className="card card-clinical">
      <div className="card-header"><Heart size={16} className="me-2" /> Clinical Decision Support</div>
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center">
          <div>
            <h6 className="mb-1">Hypertension Stage: <span className={`badge ${getStageBadge(data.stage)}`}>{data.stage || 'Unknown'}</span></h6>
            <p className="small text-muted mb-0">Avg BP: {data.average_systolic ? `${Math.round(data.average_systolic)}/${Math.round(data.average_diastolic)} mmHg` : 'No data'} • Latest: {data.latest_reading.systolic ? `${data.latest_reading.systolic}/${data.latest_reading.diastolic}` : 'N/A'}</p>
          </div>
          <div className="small text-muted">Medications: {data.current_medications?.length || 'None'}</div>
        </div>

        <div className="mt-3">
          <h6 className="small fw-semibold text-muted text-uppercase"><Pill size={14} className="me-1" /> Medication Recommendations</h6>
          {data.recommendations?.length === 0 ? <p className="small text-muted">No specific recommendations.</p> : data.recommendations.map((rec, i) => (
            <div key={i} className="p-2 bg-light rounded-3 mb-1 d-flex align-items-start gap-2">
              <span className={`badge ${rec.priority === 'URGENT' ? 'bg-danger' : rec.priority === 'HIGH' ? 'bg-warning' : rec.priority === 'MEDIUM' ? 'bg-info' : 'bg-secondary'} mt-1`}>{rec.priority}</span>
              <div><p className="small fw-semibold mb-0">{rec.recommendation}</p><p className="small text-muted mb-0">{rec.details}</p></div>
            </div>
          ))}
        </div>

        <div className="mt-3"><h6 className="small fw-semibold text-muted text-uppercase"><Microscope size={14} className="me-1" /> Suggested Investigations</h6>
          {data.labs?.length === 0 ? <p className="small text-muted">No specific tests recommended.</p> : <ul className="list-unstyled small mb-0">{data.labs.map((l, i) => <li key={i}><span className="text-primary">•</span> {l}</li>)}</ul>}
        </div>

        <div className="mt-3"><h6 className="small fw-semibold text-muted text-uppercase"><Activity size={14} className="me-1" /> Lifestyle Modifications</h6>
          {data.lifestyle?.length === 0 ? <p className="small text-muted">No specific recommendations.</p> : <ul className="list-unstyled small mb-0">{data.lifestyle.map((l, i) => <li key={i}><span className="text-primary">•</span> {l}</li>)}</ul>}
        </div>

        <details className="mt-3">
          <summary className="small fw-semibold text-muted cursor-pointer">View Clinical Summary</summary>
          <pre className="p-2 bg-light rounded-3 small text-muted mt-1" style={{ whiteSpace: 'pre-wrap' }}>{data.summary}</pre>
        </details>
      </div>
    </div>
  );
};

export default ClinicalDecisionSupport;