import { useState, useEffect } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, Activity, BarChart2, DollarSign } from 'lucide-react'

export default function MarketIntelligence() {
  const [metrics, setMetrics] = useState(null)
  const [chartData, setChartData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:8000/api/market/prices').then(res => res.json()),
      fetch('http://localhost:8000/api/market/chart').then(res => res.json())
    ])
    .then(([metricsData, chartRes]) => {
      setMetrics(metricsData)
      setChartData(chartRes)
      setLoading(false)
    })
    .catch(err => {
      console.error('Error fetching market data:', err)
      setLoading(false)
    })
  }, [])

  if (loading) return <div className="glass-panel" style={{ textAlign: 'center' }}>Loading market intelligence...</div>
  if (!metrics) return <div className="glass-panel" style={{ color: 'var(--danger)' }}>Failed to connect to backend.</div>

  return (
    <div>
      <h2 style={{ marginBottom: '20px' }}>Energy Market Intelligence</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '40px' }}>
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
            <DollarSign size={20} /> <h4>DAM Price (Avg)</h4>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--accent)' }}>
            ₹{metrics.dam_price} <span style={{ fontSize: '1rem' }}>/kWh</span>
          </div>
        </div>
        
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
            <Activity size={20} /> <h4>RTM Price</h4>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: '700', color: '#10b981' }}>
            ₹{metrics.rtm_price} <span style={{ fontSize: '1rem' }}>/kWh</span>
          </div>
        </div>

        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
            <BarChart2 size={20} /> <h4>Volume Traded</h4>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            {metrics.volume_traded.toLocaleString()} <span style={{ fontSize: '1rem' }}>MWh</span>
          </div>
        </div>
        
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
            <TrendingUp size={20} /> <h4>Price Trend</h4>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: '700', color: metrics.clearing_price_trend.startsWith('+') ? 'var(--success)' : 'var(--danger)' }}>
            {metrics.clearing_price_trend}
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ height: '400px' }}>
        <h3 style={{ marginBottom: '20px' }}>24-Hour Day-Ahead Market Prices</h3>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="var(--accent)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="hour" stroke="var(--text-secondary)" />
            <YAxis stroke="var(--text-secondary)" />
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--glass-border)' }}
            />
            <Area type="monotone" dataKey="Price" stroke="var(--accent)" fillOpacity={1} fill="url(#colorPrice)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
