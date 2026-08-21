import React, { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import { Shield, AlertCircle, CheckCircle, Activity, Loader, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const RiskAssessment = ({ patientId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRisk = async () => {
      try {
        const response = await api.get(`/analytics/risk-profile/${patientId}/`);
        setData(response.data);
      } catch (err) { setError('Could not load risk assessment.'); } finally { setLoading(false); }
    };
    if (patientId) fetchRisk();
  }, [patientId]);

  if (loading) return <div className="text-center py-3"><div className="spinner-border spinner-border-sm text-primary" /></div>;
  if (error) return <div className="text-danger text-center py-3">{error}</div>;
  if (!data) return null;

  const getRiskBadge = (category) => {
    const colors = {
      'Low': 'bg-success bg-opacity-10 text-success',
      'Low-Moderate': 'bg-info bg-opacity-10 text-info',
      'Moderate': 'bg-warning bg-opacity-10 text-warning',
      'High': 'bg-danger bg-opacity-10 text-danger',
      'Very High': 'bg-danger bg-opacity-25 text-danger',
    };
    return colors[category] || 'bg-secondary bg-opacity-10 text-secondary';
  };

  const getRiskIcon = (category) => {
    if (category === 'Low' || category === 'Low-Moderate') return <TrendingDown size={16} className="text-success" />;
    if (category === 'Moderate') return <Minus size={16} className="text-warning" />;
    if (category === 'High') return <TrendingUp size={16} className="text-danger" />;
    return <AlertCircle size={16} className="text-danger" />;
  };

  return (
    <div className="card card-clinical">
      <div className="card-header"><Shield size={16} className="me-2" /> WHO/ISH Cardiovascular Risk</div>
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center">
          <div><h6 className="mb-1">10-year risk (African region)</h6><p className="small text-muted mb-0">Based on WHO/ISH guidelines</p></div>
          <div className="text-end">
            <span className={`badge ${getRiskBadge(data.risk_category)} fs-6 px-3 py-2`}>{data.risk_percentage !== null ? `${data.risk_percentage}%` : 'N/A'}</span>
            <div className="mt-1 d-flex align-items-center gap-1 justify-content-end">
              {getRiskIcon(data.risk_category)} <span className="small fw-semibold">{data.risk_category || 'Unknown'}</span>
            </div>
          </div>
        </div>
        {!data.is_complete && <div className="mt-2 alert alert-warning py-1 small"> Complete patient profile (age, BP, smoking, diabetes, BMI) for accurate risk assessment.</div>}
        <div className="row mt-3 g-2">
          <div className="col-6">
            <div className="p-2 bg-light rounded-3">
              <h6 className="small fw-semibold text-muted text-uppercase">Risk Factors</h6>
              {data.additional_risk_factors?.length > 0 ? <ul className="list-unstyled small mb-0">{data.additional_risk_factors.map((f, i) => <li key={i}><AlertCircle size={12} className="text-warning me-1" /> {f}</li>)}</ul> : <p className="small text-muted mb-0">None identified</p>}
            </div>
          </div>
          <div className="col-6">
            <div className="p-2 bg-light rounded-3">
              <h6 className="small fw-semibold text-muted text-uppercase">Modifiable</h6>
              {data.modifiable_risk_factors?.length > 0 ? <ul className="list-unstyled small mb-0">{data.modifiable_risk_factors.map((f, i) => <li key={i}><CheckCircle size={12} className="text-success me-1" /> {f}</li>)}</ul> : <p className="small text-muted mb-0">None identified</p>}
            </div>
          </div>
        </div>
        <div className="mt-3 pt-2 border-top">
          <h6 className="small fw-semibold text-muted text-uppercase">Recommendations</h6>
          {data.recommendations?.length > 0 ? <ul className="list-unstyled small mb-0">{data.recommendations.map((r, i) => <li key={i}><span className="text-primary">•</span> {r}</li>)}</ul> : <p className="small text-muted">No specific recommendations.</p>}
        </div>
      </div>
    </div>
  );
};

export default RiskAssessment;