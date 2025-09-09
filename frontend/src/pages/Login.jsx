import React from 'react'
import { SignIn } from '@clerk/clerk-react'
import { Shield, Mountain } from 'lucide-react'

function Login() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem'
    }}>
      <div style={{
        background: 'var(--card-bg)',
        borderRadius: '16px',
        padding: '2rem',
        backdropFilter: 'blur(10px)',
        border: '1px solid var(--border-color)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        width: '100%',
        maxWidth: '400px'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Shield className="text-primary" size={40} />
            <Mountain className="text-secondary" size={36} />
          </div>
          <h1 style={{
            fontSize: '1.75rem',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '0.5rem'
          }}>
            RockFall AI Predictor
          </h1>
          <p className="text-secondary">
            Advanced AI-powered rockfall prediction and alert system for open-pit mines
          </p>
        </div>
        
        <SignIn 
          routing="path" 
          path="/login"
          redirectUrl="/dashboard"
          appearance={{
            elements: {
              rootBox: "w-full",
              card: "bg-transparent shadow-none",
              headerTitle: "text-white",
              headerSubtitle: "text-gray-400",
              socialButtonsBlockButton: "bg-gray-800 border-gray-700 text-white hover:bg-gray-700",
              formButtonPrimary: "bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600",
              footerActionLink: "text-orange-400 hover:text-orange-300"
            }
          }}
        />
        
        <div style={{
          marginTop: '1.5rem',
          padding: '1rem',
          background: 'rgba(255, 107, 53, 0.1)',
          borderRadius: '8px',
          border: '1px solid rgba(255, 107, 53, 0.2)'
        }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--primary-color)' }}>
            🔒 Secure Access
          </h3>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
            This system provides real-time rockfall risk assessment and emergency alerts for mining operations. 
            Authorized personnel only.
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login