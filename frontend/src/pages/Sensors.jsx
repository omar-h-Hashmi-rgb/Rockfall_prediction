import React, { useState, useEffect } from 'react'
import { Activity, Wifi, WifiOff, Download, RefreshCw } from 'lucide-react'
import SensorChart from '../components/sensors/SensorChart'
import DataTable from '../components/sensors/DataTable'
import { useApi } from '../hooks/useApi'

function Sensors() {
  const { get } = useApi()
  const [sensorData, setSensorData] = useState([])
  const [selectedSensor, setSelectedSensor] = useState(null)
  const [timeRange, setTimeRange] = useState(24)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSensorData()
    const interval = setInterval(loadSensorData, 60000) // Refresh every minute
    return () => clearInterval(interval)
  }, [timeRange])

  const loadSensorData = async () => {
    try {
      setLoading(true)
      const response = await get(`/sensors/data?hours=${timeRange}`)
      setSensorData(response)
      if (!selectedSensor && response.length > 0) {
        setSelectedSensor(response[0])
      }
    } catch (error) {
      console.error('Error loading sensor data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Generate sample sensor summary data
  const sensorSummary = {
    totalSensors: 20,
    activeSensors: 18,
    offlineSensors: 2,
    maintenanceSensors: 1,
    avgDisplacement: 2.4,
    avgStrain: 125.3,
    avgPorePressure: 215.7,
    avgVibration: 0.08
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Sensor Monitoring
        </h1>
        <p className="text-secondary">
          Real-time geotechnical sensor data and analysis
        </p>
      </div>

      {/* Sensor Status Overview */}
      <div className="grid grid-4 mb-4">
        <div className="card" style={{ background: 'rgba(39, 174, 96, 0.1)', border: '1px solid rgba(39, 174, 96, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <Wifi style={{ color: 'var(--success-color)' }} size={32} />
            <div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success-color)' }}>
                {sensorSummary.activeSensors}
              </h3>
              <p className="text-secondary">Active Sensors</p>
            </div>
          </div>
        </div>

        <div className="card" style={{ background: 'rgba(231, 76, 60, 0.1)', border: '1px solid rgba(231, 76, 60, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <WifiOff style={{ color: 'var(--danger-color)' }} size={32} />
            <div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--danger-color)' }}>
                {sensorSummary.offlineSensors}
              </h3>
              <p className="text-secondary">Offline Sensors</p>
            </div>
          </div>
        </div>

        <div className="card" style={{ background: 'rgba(243, 156, 18, 0.1)', border: '1px solid rgba(243, 156, 18, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <Activity style={{ color: 'var(--warning-color)' }} size={32} />
            <div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--warning-color)' }}>
                {sensorSummary.avgDisplacement}mm
              </h3>
              <p className="text-secondary">Avg Displacement</p>
            </div>
          </div>
        </div>

        <div className="card" style={{ background: 'rgba(52, 152, 219, 0.1)', border: '1px solid rgba(52, 152, 219, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <Activity style={{ color: 'var(--info-color)' }} size={32} />
            <div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--info-color)' }}>
                {sensorSummary.avgVibration}g
              </h3>
              <p className="text-secondary">Avg Vibration</p>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="card mb-4">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>Time Range:</span>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(parseInt(e.target.value))}
                style={{
                  padding: '0.5rem',
                  borderRadius: '4px',
                  border: '1px solid var(--border-color)',
                  background: 'var(--card-bg)',
                  color: 'var(--text-primary)'
                }}
              >
                <option value={1}>Last Hour</option>
                <option value={6}>Last 6 Hours</option>
                <option value={24}>Last 24 Hours</option>
                <option value={168}>Last Week</option>
              </select>
            </label>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button 
              onClick={loadSensorData} 
              className="btn btn-primary" 
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
            
            <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Download size={16} />
              Export Data
            </button>
          </div>
        </div>
      </div>

      {/* Sensor Chart */}
      <div className="card mb-4">
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
          Sensor Readings - {selectedSensor ? `Sensor ${selectedSensor.sensor_id}` : 'Select a sensor'}
        </h3>
        <SensorChart sensorData={selectedSensor} timeRange={timeRange} />
      </div>

      {/* Data Table */}
      <div className="card">
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
          Sensor Data
        </h3>
        <DataTable 
          sensorData={sensorData} 
          onSensorSelect={setSelectedSensor}
          selectedSensor={selectedSensor}
          loading={loading}
        />
      </div>
    </div>
  )
}

export default Sensors