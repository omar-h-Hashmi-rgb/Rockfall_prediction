import React from 'react'
import { UserButton, useUser } from '@clerk/clerk-react'
import { AlertTriangle, Shield } from 'lucide-react'

function Navbar() {
  const { user } = useUser()

  return (
    <nav style={{
      background: 'var(--darker-bg)',
      padding: '1rem 2rem',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      height: '70px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Shield className="text-primary" size={32} />
          <h1 style={{ 
            fontSize: '1.5rem', 
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            RockFall AI Predictor
          </h1>
        </div>
        <div style={{
          background: 'var(--danger-color)',
          color: 'white',
          padding: '0.25rem 0.75rem',
          borderRadius: '20px',
          fontSize: '0.75rem',
          fontWeight: 'bold',
          display: 'flex',
          alignItems: 'center',
          gap: '0.25rem'
        }}>
          <AlertTriangle size={14} />
          LIVE MONITORING
        </div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <span className="text-secondary">
          Welcome, {user?.firstName || 'User'}
        </span>
        <UserButton afterSignOutUrl="/login" />
      </div>
    </nav>
  )
}

export default Navbar