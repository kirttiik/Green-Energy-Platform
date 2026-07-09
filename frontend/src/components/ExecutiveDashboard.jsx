import { useState, useEffect } from 'react'

export default function ExecutiveDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch overview data from FastAPI backend
    fetch('http://localhost:8000/api/executive/overview')
      .then(res => res.json())
      .then(result => {
        setData(result)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching dashboard data:', err)
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="glass-panel" style={{ textAlign: 'center' }}>Loading dashboard data...</div>
  if (!data) return <div className="glass-panel" style={{ color: 'var(--danger)' }}>Failed to connect to backend. Make sure it is running on port 8000.</div>

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
      <div className="glass-panel">
        <h4 style={{ color: 'var(--text-secondary)' }}>Today's Generation Forecast</h4>
        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--accent)' }}>
          {data.today_forecast.toLocaleString()} <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>MWh</span>
        </div>
        <div style={{ marginTop: '8px', fontSize: '0.85rem' }}>Confidence: {data.forecast_confidence}</div>
      </div>
      
      <div className="glass-panel">
        <h4 style={{ color: 'var(--text-secondary)' }}>DAM Price Prediction</h4>
        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--accent)' }}>
          ₹{data.dam_price} <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>/kWh</span>
        </div>
      </div>

      <div className="glass-panel">
        <h4 style={{ color: 'var(--text-secondary)' }}>Est. Carbon Offset</h4>
        <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--success)' }}>
          {data.carbon_offset.toLocaleString()} <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>tons</span>
        </div>
      </div>
      
      <div className="glass-panel">
        <h4 style={{ color: 'var(--text-secondary)' }}>Plant Health Score</h4>
        <div style={{ fontSize: '2rem', fontWeight: '700', color: data.plant_health_score > 90 ? 'var(--success)' : 'var(--warning)' }}>
          {data.plant_health_score} <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>/ 100</span>
        </div>
        <div style={{ marginTop: '8px', fontSize: '0.85rem' }}>Status: {data.pipeline_health}</div>
      </div>
    </div>
  )
}
