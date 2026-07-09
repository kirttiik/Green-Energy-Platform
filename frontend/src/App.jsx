import { useState, useEffect } from 'react'
import './index.css'

import ExecutiveDashboard from './components/ExecutiveDashboard'
import GenerationChart from './components/GenerationChart'

function App() {
  const [healthStatus, setHealthStatus] = useState('Checking backend...')

  useEffect(() => {
    fetch('http://localhost:8000/api/health')
      .then(res => res.json())
      .then(data => setHealthStatus(`Backend Status: ${data.status}`))
      .catch(err => setHealthStatus('Backend Status: offline'))
  }, [])

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ marginBottom: '40px', textAlign: 'center' }}>
        <h1>Green Energy Platform</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Advanced Market Intelligence & Analytics</p>
      </header>

      <div style={{ marginBottom: '40px' }}>
        <h2 style={{ marginBottom: '20px' }}>Executive Dashboard</h2>
        <ExecutiveDashboard />
      </div>

      <div className="glass-panel" style={{ marginBottom: '40px', height: '500px' }}>
        <GenerationChart />
      </div>

      <main style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        <div className="glass-panel">
          <h3>System Status</h3>
          <p style={{ 
            color: healthStatus.includes('healthy') ? 'var(--success)' : 'var(--danger)',
            fontWeight: '500',
            marginTop: '12px'
          }}>
            {healthStatus}
          </p>
        </div>
        
        <div className="glass-panel">
          <h3>Market Insights</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '12px' }}>
            Connecting to real-time market data APIs...
          </p>
        </div>
      </main>
    </div>
  )
}

export default App
