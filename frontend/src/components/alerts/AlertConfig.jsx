import React, { useState } from 'react'
import { Save, Plus, Trash2, Mail, MessageSquare } from 'lucide-react'

function AlertConfig({ onSave }) {
  const [config, setConfig] = useState({
    emailThreshold: 0.7,
    smsThreshold: 0.8,
    recipients: [
      { name: 'Safety Manager', email: 'safety@minesite.com', phone: '+1234567890', enabled: true },
      { name: 'Operations Chief', email: 'ops@minesite.com', phone: '+1234567891', enabled: true }
    ],
    emailTemplate: {
      subject: 'ROCKFALL ALERT - {risk_class} Risk Detected',
      enabled: true
    },
    smsTemplate: {
      message: '🚨 ROCKFALL ALERT: {risk_class} risk detected ({risk_probability}% probability). Check dashboard.',
      enabled: true
    }
  })

  const handleThresholdChange = (type, value) => {
    setConfig(prev => ({
      ...prev,
      [`${type}Threshold`]: parseFloat(value)
    }))
  }

  const handleRecipientChange = (index, field, value) => {
    setConfig(prev => ({
      ...prev,
      recipients: prev.recipients.map((recipient, i) => 
        i === index ? { ...recipient, [field]: value } : recipient
      )
    }))
  }

  const addRecipient = () => {
    setConfig(prev => ({
      ...prev,
      recipients: [...prev.recipients, { name: '', email: '', phone: '', enabled: true }]
    }))
  }

  const removeRecipient = (index) => {
    setConfig(prev => ({
      ...prev,
      recipients: prev.recipients.filter((_, i) => i !== index)
    }))
  }

  const handleSave = () => {
    // In a real app, this would save to backend
    console.log('Saving alert configuration:', config)
    onSave()
  }

  return (
    <div className="grid grid-2" style={{ gap: '2rem' }}>
      {/* Alert Thresholds */}
      <div className="card">
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem' }}>
          Alert Thresholds
        </h3>
        
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
            Email Alert Threshold
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={config.emailThreshold}
            onChange={(e) => handleThresholdChange('email', e.target.value)}
            style={{ width: '100%', marginBottom: '0.5rem' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            <span>0%</span>
            <span style={{ fontWeight: 'bold', color: 'var(--primary-color)' }}>
              {(config.emailThreshold * 100).toFixed(0)}%
            </span>
            <span>100%</span>
          </div>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
            SMS Alert Threshold
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={config.smsThreshold}
            onChange={(e) => handleThresholdChange('sms', e.target.value)}
            style={{ width: '100%', marginBottom: '0.5rem' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            <span>0%</span>
            <span style={{ fontWeight: 'bold', color: 'var(--primary-color)' }}>
              {(config.smsThreshold * 100).toFixed(0)}%
            </span>
            <span>100%</span>
          </div>
        </div>

        <div className="alert-banner alert-info">
          <p style={{ fontSize: '0.875rem', margin: 0 }}>
            Alerts will be triggered when risk probability exceeds these thresholds.
            SMS threshold should typically be higher than email threshold.
          </p>
        </div>
      </div>

      {/* Message Templates */}
      <div className="card">
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem' }}>
          Message Templates
        </h3>
        
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Mail size={16} />
            <label style={{ fontWeight: '600' }}>Email Subject</label>
          </div>
          <input
            type="text"
            value={config.emailTemplate.subject}
            onChange={(e) => setConfig(prev => ({
              ...prev,
              emailTemplate: { ...prev.emailTemplate, subject: e.target.value }
            }))}
            style={{
              width: '100%',
              padding: '0.75rem',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: 'var(--card-bg)',
              color: 'var(--text-primary)'
            }}
          />
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <MessageSquare size={16} />
            <label style={{ fontWeight: '600' }}>SMS Message</label>
          </div>
          <textarea
            value={config.smsTemplate.message}
            onChange={(e) => setConfig(prev => ({
              ...prev,
              smsTemplate: { ...prev.smsTemplate, message: e.target.value }
            }))}
            rows={3}
            style={{
              width: '100%',
              padding: '0.75rem',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: 'var(--card-bg)',
              color: 'var(--text-primary)',
              resize: 'vertical'
            }}
          />
        </div>

        <div className="alert-banner alert-info">
          <p style={{ fontSize: '0.875rem', margin: 0 }}>
            Use placeholders: {'{risk_class}'}, {'{risk_probability}'}, {'{sector}'}, {'{timestamp}'}
          </p>
        </div>
      </div>

      {/* Recipients */}
      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600' }}>
            Alert Recipients
          </h3>
          <button onClick={addRecipient} className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Plus size={16} />
            Add Recipient
          </button>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Name</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Email</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Phone</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Status</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {config.recipients.map((recipient, index) => (
                <tr key={index} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.75rem' }}>
                    <input
                      type="text"
                      value={recipient.name}
                      onChange={(e) => handleRecipientChange(index, 'name', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        borderRadius: '4px',
                        border: '1px solid var(--border-color)',
                        background: 'var(--card-bg)',
                        color: 'var(--text-primary)'
                      }}
                    />
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <input
                      type="email"
                      value={recipient.email}
                      onChange={(e) => handleRecipientChange(index, 'email', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        borderRadius: '4px',
                        border: '1px solid var(--border-color)',
                        background: 'var(--card-bg)',
                        color: 'var(--text-primary)'
                      }}
                    />
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <input
                      type="tel"
                      value={recipient.phone}
                      onChange={(e) => handleRecipientChange(index, 'phone', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        borderRadius: '4px',
                        border: '1px solid var(--border-color)',
                        background: 'var(--card-bg)',
                        color: 'var(--text-primary)'
                      }}
                    />
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <input
                        type="checkbox"
                        checked={recipient.enabled}
                        onChange={(e) => handleRecipientChange(index, 'enabled', e.target.checked)}
                      />
                      <span style={{ fontSize: '0.875rem' }}>
                        {recipient.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </label>
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <button
                      onClick={() => removeRecipient(index)}
                      className="btn btn-danger"
                      style={{ padding: '0.5rem', fontSize: '0.875rem' }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Save Button */}
      <div className="card" style={{ gridColumn: '1 / -1', textAlign: 'center' }}>
        <button onClick={handleSave} className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem', padding: '1rem 2rem' }}>
          <Save size={20} />
          Save Configuration
        </button>
      </div>
    </div>
  )
}

export default AlertConfig