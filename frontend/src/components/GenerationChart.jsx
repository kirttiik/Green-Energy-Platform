import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function GenerationChart() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/executive/generation-chart')
      .then(res => res.json())
      .then(result => {
        setData(result)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching chart data:', err)
        setLoading(false)
      })
  }, [])

  if (loading) return <div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading chart...</div>

  return (
    <div style={{ width: '100%', height: 400 }}>
      <h3 style={{ marginBottom: '20px', color: 'var(--text-primary)' }}>Hourly Solar + Wind Generation Profile</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="hour" stroke="var(--text-secondary)" />
          <YAxis stroke="var(--text-secondary)" label={{ value: 'Generation (MW)', angle: -90, position: 'insideLeft', fill: 'var(--text-secondary)' }} />
          <Tooltip 
            contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--glass-border)', borderRadius: '8px' }}
            itemStyle={{ color: 'var(--text-primary)' }}
          />
          <Legend />
          <Bar dataKey="Solar" stackId="a" fill="#FFB347" />
          <Bar dataKey="Wind" stackId="a" fill="#5B9BD5" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
