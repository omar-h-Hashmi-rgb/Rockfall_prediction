import React from 'react'
import { RefreshCw, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { format } from 'date-fns'

function AlertHistory({ alerts, loading, onRefresh }) {
  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600' }}>
          Recent Alerts
        </h3>
        <button onClick={onRefresh} className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {alerts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <AlertTriangle size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
          <p>No alerts found</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '1rem', textAlign: 'left' }}>Time</th>
                <th style={{ padding: '1rem', textAlign: 'left' }}>Risk Level</th>
                <th style={{ padding: '1rem', textAlign: 'left' }}>Probability</th>
                <th style={{ padding: '1rem', textAlign: 'left' }}>Location</th>
                <th style={{ padding: '1rem', textAlign: 'left' }}>Email</th>
                <th style={{ padding: '1rem', textAlign: 'left' }}>SMS</th>
                <th style={{ padding: '1rem', textAlign: 'left' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert, index) => (
                <tr key={index} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '1rem' }}>
                    {format(new Date(alert.timestamp), 'MMM dd, HH:mm')}
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className={`status-indicator status-${alert.risk_class?.toLowerCase()}`}></span>
                      {alert.risk_class}
                    </div>
                  </td>
                  <td style={{ padding: '1rem' }}>
                    {(alert.risk_probability * 100).toFixed(1)}%
                  </td>
                  <td style={{ padding: '1rem' }}>
                    Sector {alert.sector || 'Unknown'}
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {alert.results?.email_sent > 0 ? (
                        <CheckCircle className="text-success" size={16} />
                      ) : alert.results?.email_failed > 0 ? (
                        <XCircle className="text-danger" size={16} />
                      ) : (
                        <span className="text-muted">-</span>
                      )}
                      <span>{alert.results?.email_sent || 0}</span>
                    </div>
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {alert.results?.sms_sent > 0 ? (
                        <CheckCircle className="text-success" size={16} />
                      ) : alert.results?.sms_failed > 0 ? (
                        <XCircle className="text-danger" size={16} />
                      ) : (
                        <span className="text-muted">-</span>
                      )}
                      <span>{alert.results?.sms_sent || 0}</span>
                    </div>
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <span className={`btn ${alert.status === 'sent' ? 'btn-success' : 'btn-warning'}`} 
                          style={{ fontSize: '0.75rem', padding: '0.25rem 0.75rem' }}>
                      {alert.status || 'Pending'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default AlertHistory