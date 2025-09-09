import React from 'react'
import { TrendingUp, AlertTriangle, Activity, Shield } from 'lucide-react'

function QuickStats({ stats }) {
  const riskStats = stats?.risk_statistics || {}
  const totalPredictions = stats?.total_predictions || 0
  const totalAlerts = stats?.total_alerts || 0
  const sensorCount = stats?.recent_sensor_count || 0

  const highRiskCount = riskStats.High?.count || 0
  const mediumRiskCount = riskStats.Medium?.count || 0
  const lowRiskCount = riskStats.Low?.count || 0

  const statCards = [
    {
      title: 'High Risk Events',
      value: highRiskCount,
      icon: AlertTriangle,
      color: 'var(--danger-color)',
      bgColor: 'rgba(231, 76, 60, 0.1)'
    },
    {
      title: 'Total Predictions',
      value: totalPredictions,
      icon: TrendingUp,
      color: 'var(--primary-color)',
      bgColor: 'rgba(255, 107, 53, 0.1)'
    },
    {
      title: 'Active Sensors',
      value: sensorCount,
      icon: Activity,
      color: 'var(--success-color)',
      bgColor: 'rgba(39, 174, 96, 0.1)'
    },
    {
      title: 'Alerts Sent',
      value: totalAlerts,
      icon: Shield,
      color: 'var(--warning-color)',
      bgColor: 'rgba(243, 156, 18, 0.1)'
    }
  ]

  return (
    <>
      {statCards.map((stat, index) => (
        <div key={index} className="card" style={{ 
          background: stat.bgColor,
          border: `1px solid ${stat.color}40`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                {stat.title}
              </p>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: stat.color }}>
                {stat.value}
              </p>
            </div>
            <stat.icon size={40} style={{ color: stat.color, opacity: 0.7 }} />
          </div>
        </div>
      ))}
    </>
  )
}

export default QuickStats