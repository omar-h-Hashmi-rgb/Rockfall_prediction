import React from 'react'
import { Wifi, WifiOff, AlertTriangle } from 'lucide-react'

function DataTable({ sensorData, onSensorSelect, selectedSensor, loading }) {
  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  // Generate sample sensor list since we don't have real data structure
  const sampleSensors = Array.from({ length: 20 }, (_, index) => ({
    id: `SENSOR_${(index + 1).toString().padStart(3, '0')}`,
    name: `Geotechnical Sensor ${index + 1}`,
    location: `Sector ${Math.floor(index / 5) + 1}`,
    status: Math.random() > 0.1 ? 'online' : 'offline',
    lastReading: new Date(Date.now() - Math.random() * 3600000).toISOString(),
    displacement: (Math.random() * 5).toFixed(2),
    strain: (Math.random() * 200 + 50).toFixed(1),
    porePressure: (Math.random() * 150 + 150).toFixed(1),
    vibration: (Math.random() * 0.2).toFixed(3),
    batteryLevel: Math.floor(Math.random() * 100),
    riskLevel: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)]
  }))

  const getStatusIcon = (status) => {
    return status === 'online' ? 
      <Wifi className="text-success" size={16} /> : 
      <WifiOff className="text-danger" size={16} />
  }

  const getStatusColor = (status) => {
    return status === 'online' ? 'var(--success-color)' : 'var(--danger-color)'
  }

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'High': return 'var(--danger-color)'
      case 'Medium': return 'var(--warning-color)'
      case 'Low': return 'var(--success-color)'
      default: return 'var(--text-muted)'
    }
  }

  const getBatteryColor = (level) => {
    if (level > 50) return 'var(--success-color)'
    if (level > 20) return 'var(--warning-color)'
    return 'var(--danger-color)'
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Sensor ID</th>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Location</th>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Status</th>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Displacement</th>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Strain</th>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Pressure</th>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Vibration</th>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Battery</th>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Risk</th>
            <th style={{ padding: '1rem', textAlign: 'left' }}>Last Reading</th>
          </tr>
        </thead>
        <tbody>
          {sampleSensors.map((sensor, index) => (
            <tr 
              key={index} 
              style={{ 
                borderBottom: '1px solid var(--border-color)',
                backgroundColor: selectedSensor?.id === sensor.id ? 'rgba(255, 107, 53, 0.1)' : 'transparent',
                cursor: 'pointer'
              }}
              onClick={() => onSensorSelect(sensor)}
            >
              <td style={{ padding: '1rem' }}>
                <div style={{ fontWeight: '600' }}>{sensor.id}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{sensor.name}</div>
              </td>
              <td style={{ padding: '1rem' }}>{sensor.location}</td>
              <td style={{ padding: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {getStatusIcon(sensor.status)}
                  <span style={{ color: getStatusColor(sensor.status), fontWeight: '500' }}>
                    {sensor.status}
                  </span>
                </div>
              </td>
              <td style={{ padding: '1rem' }}>
                <span style={{ fontWeight: '500' }}>{sensor.displacement}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> mm</span>
              </td>
              <td style={{ padding: '1rem' }}>
                <span style={{ fontWeight: '500' }}>{sensor.strain}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> μs</span>
              </td>
              <td style={{ padding: '1rem' }}>
                <span style={{ fontWeight: '500' }}>{sensor.porePressure}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> kPa</span>
              </td>
              <td style={{ padding: '1rem' }}>
                <span style={{ fontWeight: '500' }}>{sensor.vibration}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> g</span>
              </td>
              <td style={{ padding: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{
                    width: '40px',
                    height: '8px',
                    background: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: '4px',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      width: `${sensor.batteryLevel}%`,
                      height: '100%',
                      background: getBatteryColor(sensor.batteryLevel)
                    }}></div>
                  </div>
                  <span style={{ fontSize: '0.75rem' }}>{sensor.batteryLevel}%</span>
                </div>
              </td>
              <td style={{ padding: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span className={`status-indicator status-${sensor.riskLevel.toLowerCase()}`}></span>
                  <span style={{ color: getRiskColor(sensor.riskLevel), fontWeight: '500' }}>
                    {sensor.riskLevel}
                  </span>
                  {sensor.riskLevel === 'High' && <AlertTriangle size={14} style={{ color: 'var(--danger-color)' }} />}
                </div>
              </td>
              <td style={{ padding: '1rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                {new Date(sensor.lastReading).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default DataTable