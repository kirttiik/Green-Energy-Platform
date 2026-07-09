import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'

import Sidebar from './components/Sidebar'
import ExecutiveDashboard from './components/ExecutiveDashboard'
import GenerationChart from './components/GenerationChart'
import WeatherIntelligence from './components/WeatherIntelligence'
import MarketIntelligence from './components/MarketIntelligence'

function ExecutivePage() {
  return (
    <>
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{ marginBottom: '20px' }}>Executive Control Center</h2>
        <ExecutiveDashboard />
      </div>
      <div className="glass-panel" style={{ marginBottom: '40px', height: '500px' }}>
        <GenerationChart />
      </div>
    </>
  )
}

function PlaceholderPage({ title }) {
  return (
    <div className="glass-panel" style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px' }}>
      <h2 style={{ margin: 0 }}>{title}</h2>
      <p style={{ color: 'var(--text-secondary)' }}>Module migration in progress...</p>
    </div>
  )
}

function App() {
  const [healthStatus, setHealthStatus] = useState('Checking backend...')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/health')
      .then(res => res.json())
      .then(data => setHealthStatus(`Backend: ${data.status}`))
      .catch(err => setHealthStatus('Backend: offline'))
  }, [])

  return (
    <Router>
      <div style={{ display: 'flex', minHeight: '100vh', padding: '24px', gap: '32px', maxWidth: '1600px', margin: '0 auto' }}>
        <Sidebar />
        
        <div style={{ flex: 1, paddingBottom: '60px' }}>
          <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
            <div>
              <h1 style={{ fontSize: '2rem', margin: 0 }}>Green Energy Platform</h1>
              <p style={{ color: 'var(--text-secondary)' }}>Advanced Market Intelligence & Analytics</p>
            </div>
            <div className="glass-panel" style={{ padding: '8px 16px', borderRadius: '20px' }}>
              <span style={{ 
                color: healthStatus.includes('healthy') ? 'var(--success)' : 'var(--danger)',
                fontSize: '0.85rem',
                fontWeight: '500'
              }}>
                ● {healthStatus}
              </span>
            </div>
          </header>

          <main>
            <Routes>
              <Route path="/" element={<ExecutivePage />} />
              <Route path="/digital-twin" element={<PlaceholderPage title="Digital Twin" />} />
              <Route path="/portfolio" element={<PlaceholderPage title="Portfolio Analytics" />} />
              <Route path="/performance" element={<PlaceholderPage title="Plant Performance" />} />
              <Route path="/operations" element={<PlaceholderPage title="Operations & Maint" />} />
              <Route path="/forecast" element={<PlaceholderPage title="Generation Forecast" />} />
              <Route path="/weather" element={<WeatherIntelligence />} />
              <Route path="/sustainability" element={<PlaceholderPage title="Sustainability Analytics" />} />
              <Route path="/market" element={<MarketIntelligence />} />
              <Route path="/grid" element={<PlaceholderPage title="Grid Intelligence" />} />
              <Route path="/explainability" element={<PlaceholderPage title="AI Explainability" />} />
              <Route path="/shap" element={<PlaceholderPage title="SHAP Analytics" />} />
              <Route path="/mlops" element={<PlaceholderPage title="MLOps Hub" />} />
              <Route path="/copilot" element={<PlaceholderPage title="AI Operations Copilot" />} />
              <Route path="/health" element={<PlaceholderPage title="Platform Health" />} />
              <Route path="/about" element={<PlaceholderPage title="About Platform" />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App
