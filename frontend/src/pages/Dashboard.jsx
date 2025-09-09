import React, { useState, useEffect } from 'react'
import { AlertTriangle, Activity, MapPin, Clock } from 'lucide-react'
import RiskMap from '../components/dashboard/RiskMap'
import ForecastChart from '../components/dashboard/ForecastChart'
import QuickStats from '../components/dashboard/QuickStats'
import { useApi } from '../hooks/useApi'

function Dashboard() {
  const { get } = useApi()
  const [stats, setStats] = useState(null)
  const [recentPredictions, setRecentPredictions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
    const interval = setInterval(loadDashboardData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [statsResponse, predictionsResponse] = await Promise.all([
        get('/dashboard/stats'),
        get('/predictions/recent?limit=10')
      ])
      
      setStats(statsResponse)
      setRecentPredictions(predictionsResponse)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  const currentRisk = recentPredictions[0]?.risk_class || 'Low'
  const currentProbability = recentPredictions[0]?.risk_probability || 0

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Mining Operations Dashboard
        </h1>
        <p className="text-secondary">
          Real-time rockfall risk monitoring and prediction system
        </p>
      </div>

      {/* Current Risk Alert */}
      {currentRisk === 'High' && (
        <div className="alert-banner alert-danger">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertTriangle size={20} />
            <strong>HIGH RISK ALERT:</strong> Immediate attention required. Risk probability: {(currentProbability * 100).toFixed(1)}%
          </div>
        </div>
      )}

      {currentRisk === 'Medium' && (
        <div className="alert-banner alert-warning">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertTriangle size={20} />
            <strong>MEDIUM RISK:</strong> Monitor conditions closely. Risk probability: {(currentProbability * 100).toFixed(1)}%
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-4 mb-4">
        <QuickStats stats={stats} />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-2 mb-4">
        {/* Risk Map */}
        <div className="card">
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            Risk Heat Map
          </h3>
          <RiskMap predictions={recentPredictions} />
        </div>

        {/* Current Status */}
        <div className="card">
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            Current Status
          </h3>
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div style={{
              width: '120px',
              height: '120px',
              borderRadius: '50%',
              background: currentRisk === 'High' ? 'var(--danger-color)' : 
                         currentRisk === 'Medium' ? 'var(--warning-color)' : 'var(--success-color)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1rem',
              fontSize: '1.5rem',
              fontWeight: 'bold'
            }}>
              {(currentProbability * 100).toFixed(0)}%
            </div>
            <h4 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
              {currentRisk} Risk
            </h4>
            <p className="text-secondary">
              Current risk assessment based on latest sensor data and AI analysis
            </p>
          </div>
        </div>
      </div>

      {/* Forecast Chart */}
      <div className="card mb-4">
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
          Risk Forecast (24 Hours)
        </h3>
        <ForecastChart predictions={recentPredictions} />
      </div>

      {/* Recent Predictions Table */}
      <div className="card">
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
          Recent Predictions
        </h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Time</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Risk Level</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Probability</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Location</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentPredictions.slice(0, 5).map((prediction, index) => (
                <tr key={index} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem' }}>
                    {new Date(prediction.timestamp).toLocaleTimeString()}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className={`status-indicator status-${prediction.risk_class?.toLowerCase()}`}></span>
                      {prediction.risk_class}
                    </div>
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    {(prediction.risk_probability * 100).toFixed(1)}%
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    Sector {prediction.coordinates?.sector || 'Unknown'}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    {prediction.alert_required ? 
                      <span className="text-danger">Alert Sent</span> : 
                      <span className="text-success">Normal</span>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Dashboard