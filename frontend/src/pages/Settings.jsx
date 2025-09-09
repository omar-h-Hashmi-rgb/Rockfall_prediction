import React, { useState } from 'react'
import { Save, User, Bell, Shield, Database, Download } from 'lucide-react'

function Settings() {
  const [settings, setSettings] = useState({
    user: {
      name: 'John Doe',
      email: 'john.doe@minesite.com',
      role: 'Safety Manager',
      phone: '+1234567890'
    },
    notifications: {
      emailAlerts: true,
      smsAlerts: true,
      browserNotifications: true,
      alertThreshold: 0.7,
      maintenanceReminders: true
    },
    system: {
      dataRetention: 365,
      backupFrequency: 'daily',
      apiRateLimit: 1000,
      logLevel: 'info'
    },
    security: {
      sessionTimeout: 480,
      requireMFA: true,
      passwordExpiry: 90,
      ipWhitelist: ''
    }
  })

  const [activeTab, setActiveTab] = useState('user')

  const handleInputChange = (section, field, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }))
  }

  const handleSave = () => {
    // In real app, save to backend
    console.log('Saving settings:', settings)
    alert('Settings saved successfully!')
  }

  const tabs = [
    { id: 'user', label: 'User Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'system', label: 'System', icon: Database },
    { id: 'security', label: 'Security', icon: Shield }
  ]

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          System Settings
        </h1>
        <p className="text-secondary">
          Configure system preferences and user settings
        </p>
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

      {/* User Profile Tab */}
      {activeTab === 'user' && (
        <div className="card">
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem' }}>
            User Profile
          </h3>
          
          <div className="grid grid-2" style={{ gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                Full Name
              </label>
              <input
                type="text"
                value={settings.user.name}
                onChange={(e) => handleInputChange('user', 'name', e.target.value)}
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
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                Email Address
              </label>
              <input
                type="email"
                value={settings.user.email}
                onChange={(e) => handleInputChange('user', 'email', e.target.value)}
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
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                Role
              </label>
              <select
                value={settings.user.role}
                onChange={(e) => handleInputChange('user', 'role', e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color)',
                  background: 'var(--card-bg)',
                  color: 'var(--text-primary)'
                }}
              >
                <option value="Safety Manager">Safety Manager</option>
                <option value="Operations Manager">Operations Manager</option>
                <option value="System Administrator">System Administrator</option>
                <option value="Geotechnical Engineer">Geotechnical Engineer</option>
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                Phone Number
              </label>
              <input
                type="tel"
                value={settings.user.phone}
                onChange={(e) => handleInputChange('user', 'phone', e.target.value)}
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
          </div>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="card">
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem' }}>
            Notification Preferences
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={settings.notifications.emailAlerts}
                  onChange={(e) => handleInputChange('notifications', 'emailAlerts', e.target.checked)}
                />
                <div>
                  <div style={{ fontWeight: '600' }}>Email Alerts</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                    Receive risk alerts via email
                  </div>
                </div>
              </label>
            </div>
            
            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={settings.notifications.smsAlerts}
                  onChange={(e) => handleInputChange('notifications', 'smsAlerts', e.target.checked)}
                />
                <div>
                  <div style={{ fontWeight: '600' }}>SMS Alerts</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                    Receive critical alerts via SMS
                  </div>
                </div>
              </label>
            </div>
            
            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={settings.notifications.browserNotifications}
                  onChange={(e) => handleInputChange('notifications', 'browserNotifications', e.target.checked)}
                />
                <div>
                  <div style={{ fontWeight: '600' }}>Browser Notifications</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                    Show notifications in browser
                  </div>
                </div>
              </label>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                Alert Threshold: {(settings.notifications.alertThreshold * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={settings.notifications.alertThreshold}
                onChange={(e) => handleInputChange('notifications', 'alertThreshold', parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
              <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Trigger alerts when risk probability exceeds this threshold
              </div>
            </div>
          </div>
        </div>
      )}

      {/* System Tab */}
      {activeTab === 'system' && (
        <div className="card">
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem' }}>
            System Configuration
          </h3>
          
          <div className="grid grid-2" style={{ gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                Data Retention (days)
              </label>
              <input
                type="number"
                value={settings.system.dataRetention}
                onChange={(e) => handleInputChange('system', 'dataRetention', parseInt(e.target.value))}
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
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                Backup Frequency
              </label>
              <select
                value={settings.system.backupFrequency}
                onChange={(e) => handleInputChange('system', 'backupFrequency', e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color)',
                  background: 'var(--card-bg)',
                  color: 'var(--text-primary)'
                }}
              >
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                API Rate Limit (requests/hour)
              </label>
              <input
                type="number"
                value={settings.system.apiRateLimit}
                onChange={(e) => handleInputChange('system', 'apiRateLimit', parseInt(e.target.value))}
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
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                Log Level
              </label>
              <select
                value={settings.system.logLevel}
                onChange={(e) => handleInputChange('system', 'logLevel', e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color)',
                  background: 'var(--card-bg)',
                  color: 'var(--text-primary)'
                }}
              >
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>
          
          <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem' }}>
              System Actions
            </h4>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Download size={16} />
                Export System Data
              </button>
              <button className="btn btn-warning" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Database size={16} />
                Clear Cache
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="card">
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem' }}>
            Security Settings
          </h3>
          
          <div className="grid grid-2" style={{ gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                Session Timeout (minutes)
              </label>
              <input
                type="number"
                value={settings.security.sessionTimeout}
                onChange={(e) => handleInputChange('security', 'sessionTimeout', parseInt(e.target.value))}
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
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
                Password Expiry (days)
              </label>
              <input
                type="number"
                value={settings.security.passwordExpiry}
                onChange={(e) => handleInputChange('security', 'passwordExpiry', parseInt(e.target.value))}
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
          </div>
          
          <div style={{ marginTop: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={settings.security.requireMFA}
                onChange={(e) => handleInputChange('security', 'requireMFA', e.target.checked)}
              />
              <div>
                <div style={{ fontWeight: '600' }}>Require Multi-Factor Authentication</div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                  Require additional authentication for login
                </div>
              </div>
            </label>
          </div>
          
          <div style={{ marginTop: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
              IP Whitelist (one per line)
            </label>
            <textarea
              value={settings.security.ipWhitelist}
              onChange={(e) => handleInputChange('security', 'ipWhitelist', e.target.value)}
              placeholder="192.168.1.0/24&#10;10.0.0.0/8"
              rows={4}
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
        </div>
      )}

      {/* Save Button */}
      <div className="card mt-4" style={{ textAlign: 'center' }}>
        <button 
          onClick={handleSave} 
          className="btn btn-primary" 
          style={{ 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: '0.5rem', 
            fontSize: '1rem', 
            padding: '1rem 2rem' 
          }}
        >
          <Save size={20} />
          Save Settings
        </button>
      </div>
    </div>
  )
}

export default Settings