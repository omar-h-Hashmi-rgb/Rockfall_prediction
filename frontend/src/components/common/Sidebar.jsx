import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  AlertTriangle, 
  Camera, 
  Activity, 
  Settings,
  MapPin
} from 'lucide-react'

const navigationItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/alerts', icon: AlertTriangle, label: 'Alerts' },
  { to: '/imagery', icon: Camera, label: 'Drone Imagery' },
  { to: '/sensors', icon: Activity, label: 'Sensors' },
  { to: '/settings', icon: Settings, label: 'Settings' }
]

function Sidebar() {
  return (
    <aside style={{
      width: '250px',
      background: 'var(--card-bg)',
      borderRight: '1px solid var(--border-color)',
      padding: '2rem 0'
    }}>
      <nav style={{ padding: '0 1rem' }}>
        {navigationItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.875rem 1rem',
              borderRadius: '8px',
              textDecoration: 'none',
              color: isActive ? 'var(--primary-color)' : 'var(--text-secondary)',
              background: isActive ? 'rgba(255, 107, 53, 0.1)' : 'transparent',
              marginBottom: '0.5rem',
              transition: 'all 0.3s ease',
              fontWeight: isActive ? '600' : '400'
            })}
          >
            <item.icon size={20} />
            {item.label}
          </NavLink>
        ))}
      </nav>
      
      <div style={{
        marginTop: '2rem',
        padding: '1rem',
        borderTop: '1px solid var(--border-color)'
      }}>
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <MapPin className="text-primary" size={16} />
            <span style={{ fontSize: '0.875rem', fontWeight: '600' }}>Mine Location</span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Sector 7, Open Pit Mine<br />
            Coordinates: 28.6139°N, 77.2090°E
          </p>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar