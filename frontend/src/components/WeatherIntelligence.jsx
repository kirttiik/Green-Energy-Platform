import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { CloudRain, Sun, Wind, Thermometer } from 'lucide-react'

export default function WeatherIntelligence() {
  const [metrics, setMetrics] = useState(null)
  const [forecast, setForecast] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('http://127.0.0.1:8000/api/weather/metrics').then(res => res.json()),
      fetch('http://127.0.0.1:8000/api/weather/forecast').then(res => res.json())
    ])
    .then(([metricsData, forecastData]) => {
      setMetrics(metricsData)
      setForecast(forecastData)
      setLoading(false)
    })
    .catch(err => {
      console.error('Error fetching weather data:', err)
      setLoading(false)
    })
  }, [])

  if (loading) return <div className="glass-panel" style={{ textAlign: 'center' }}>Loading weather intelligence...</div>
  if (!metrics) return <div className="glass-panel" style={{ color: 'var(--danger)' }}>Failed to connect to backend.</div>

  return (
    <div>
      <h2 style={{ marginBottom: '20px' }}>Weather Intelligence & Analytics</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '40px' }}>
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
            <Thermometer size={20} /> <h4>Temperature</h4>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--accent)' }}>
            {metrics.current_temperature}°C
          </div>
        </div>
        
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
            <Sun size={20} /> <h4>Irradiance</h4>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: '700', color: '#FFB347' }}>
            {metrics.solar_irradiance} <span style={{ fontSize: '1rem' }}>W/m²</span>
          </div>
        </div>

        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
            <Wind size={20} /> <h4>Wind Speed</h4>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: '700', color: '#5B9BD5' }}>
            {metrics.wind_speed} <span style={{ fontSize: '1rem' }}>m/s</span>
          </div>
        </div>
        
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
            <CloudRain size={20} /> <h4>Cloud Cover</h4>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            {metrics.cloud_cover}
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ height: '400px' }}>
        <h3 style={{ marginBottom: '20px' }}>7-Day Weather Forecast (Irradiance)</h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={forecast} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="day" stroke="var(--text-secondary)" />
            <YAxis stroke="var(--text-secondary)" />
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--glass-border)' }}
            />
            <Legend />
            <Line type="monotone" dataKey="irradiance" stroke="#FFB347" strokeWidth={3} dot={{ r: 5 }} activeDot={{ r: 8 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
