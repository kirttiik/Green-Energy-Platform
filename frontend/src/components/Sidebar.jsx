import { NavLink } from 'react-router-dom'
import { 
  Home, Map, PieChart, Activity, Wrench, LineChart, 
  CloudRain, Leaf, TrendingUp, Zap, BrainCircuit, 
  Microscope, Settings, Bot, ShieldCheck, Info
} from 'lucide-react'

const navItems = [
  { path: '/', label: 'Executive Control Center', icon: Home },
  { path: '/digital-twin', label: 'Digital Twin', icon: Map },
  { path: '/portfolio', label: 'Portfolio Analytics', icon: PieChart },
  { path: '/performance', label: 'Plant Performance', icon: Activity },
  { path: '/operations', label: 'Operations & Maint', icon: Wrench },
  { path: '/forecast', label: 'Generation Forecast', icon: LineChart },
  { path: '/weather', label: 'Weather Intelligence', icon: CloudRain },
  { path: '/sustainability', label: 'Sustainability', icon: Leaf },
  { path: '/market', label: 'Market Intelligence', icon: TrendingUp },
  { path: '/grid', label: 'Grid Intelligence', icon: Zap },
  { path: '/explainability', label: 'AI Explainability', icon: BrainCircuit },
  { path: '/shap', label: 'SHAP Analytics', icon: Microscope },
  { path: '/mlops', label: 'MLOps Hub', icon: Settings },
  { path: '/copilot', label: 'AI Copilot', icon: Bot },
  { path: '/health', label: 'Platform Health', icon: ShieldCheck },
  { path: '/about', label: 'About Platform', icon: Info },
]

export default function Sidebar() {
  return (
    <div className="glass-panel" style={{ 
      width: '280px', 
      height: 'calc(100vh - 48px)', 
      position: 'sticky', 
      top: '24px',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 16px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px', padding: '0 8px' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: 'var(--accent-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Zap size={24} color="white" />
        </div>
        <div>
          <h2 style={{ fontSize: '1.1rem', margin: 0, lineHeight: 1.2 }}>Khavda Twin</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>v1.0.0 | Production</span>
        </div>
      </div>
      
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {navItems.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '12px 16px',
              borderRadius: '8px',
              color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              background: isActive ? 'rgba(255,255,255,0.05)' : 'transparent',
              border: isActive ? '1px solid rgba(255,255,255,0.1)' : '1px solid transparent',
              fontWeight: isActive ? '500' : '400',
              transition: 'all 0.2s ease',
              textDecoration: 'none'
            })}
          >
            <item.icon size={18} style={{ opacity: 0.8 }} />
            <span style={{ fontSize: '0.9rem' }}>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
