import React, { useState, useEffect } from 'react'
import { AlertTriangle, Mail, MessageSquare, Settings, Clock } from 'lucide-react'
import AlertConfig from '../components/alerts/AlertConfig'
import AlertHistory from '../components/alerts/AlertHistory'
import { useApi } from '../hooks/useApi'

function Alerts() {
  const { get } = useApi()
  const [alerts, setAlerts] = useState([])
  const [activeTab, setActiveTab] = useState('history')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAlerts()
  }, [])

  const loadAlerts = async () => {
    try {
      setLoading(true)
      const response = await get('/alerts/recent')
      setAlerts(response)
    } catch (error) {
      console.error('Error loading alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'history', label: 'Alert History', icon: Clock },
    { id: 'config', label: 'Configuration', icon: Settings }
  ]

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Alert Management
        </h1>
        <p className="text-secondary">
          Configure alert settings and monitor notification history
        </p>
      </div>

      {/* Alert Summary Cards */}
      <div className="grid grid-3 mb-4">
        <div className="card" style={{ background: 'rgba(231, 76, 60, 0.1)', border: '1px solid rgba(231, 76, 60, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <AlertTriangle style={{ color: 'var(--danger-color)' }} size={32} />
            <div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--danger-color)' }}>
                {alerts.filter(a => a.risk_class === 'High').length}
              </h3>
              <p className="text-secondary">High Risk Alerts</p>
            </div>
          </div>
        </div>

        <div className="card" style={{ background: 'rgba(39, 174, 96, 0.1)', border: '1px solid rgba(39, 174, 96, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <Mail style={{ color: 'var(--success-color)' }} size={32} />
            <div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success-color)' }}>
                {alerts.filter(a => a.results?.email_sent > 0).length}
              </h3>
              <p className="text-secondary">Emails Sent</p>
            </div>
          </div>
        </div>

        <div className="card" style={{ background: 'rgba(52, 152, 219, 0.1)', border: '1px solid rgba(52, 152, 219, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <MessageSquare style={{ color: 'var(--info-color)' }} size={32} />
            <div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--info-color)' }}>
                {alerts.filter(a => a.results?.sms_sent > 0).length}
              </h3>
              <p className="text-secondary">SMS Sent</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{ 
        display: 'flex', 
        gap: '1rem', 
        marginBottom: '2rem',
        borderBottom: '1px solid var(--border-color)',
        paddingBottom: '1rem'
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`btn ${activeTab === tab.id ? 'btn-primary' : ''}`}
            style={{
              background: activeTab === tab.id ? 'var(--primary-color)' : 'transparent',
              color: activeTab === tab.id ? 'white' : 'var(--text-secondary)',
              border: '1px solid var(--border-color)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'history' && (
        <AlertHistory alerts={alerts} loading={loading} onRefresh={loadAlerts} />
      )}
      
      {activeTab === 'config' && (
        <AlertConfig onSave={loadAlerts} />
      )}
    </div>
  )
}

export default Alerts