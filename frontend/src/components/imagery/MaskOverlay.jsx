import React from 'react'
import { Layers, Eye, EyeOff } from 'lucide-react'

function MaskOverlay({ image }) {
  if (!image?.maskAvailable) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <EyeOff size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
        <p className="text-muted">No mask data available for this image</p>
      </div>
    )
  }

  // Simulate mask analysis data
  const maskAnalysis = {
    riskAreas: [
      { type: 'High Risk', percentage: 15, color: '#e74c3c', description: 'Steep slopes with loose material' },
      { type: 'Medium Risk', percentage: 35, color: '#f39c12', description: 'Moderate slope instability' },
      { type: 'Low Risk', percentage: 50, color: '#27ae60', description: 'Stable terrain' }
    ],
    features: {
      cracksDetected: 12,
      unstableSlopes: 8,
      vegetationCover: 25,
      rockExposure: 75
    }
  }

  return (
    <div className="card">
      <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Layers size={20} />
        Risk Mask Analysis
      </h3>

      {/* Risk Distribution */}
      <div style={{ marginBottom: '2rem' }}>
        <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem' }}>
          Risk Distribution
        </h4>
        
        <div style={{ marginBottom: '1rem' }}>
          {maskAnalysis.riskAreas.map((area, index) => (
            <div key={index} style={{ marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{
                    width: '12px',
                    height: '12px',
                    background: area.color,
                    borderRadius: '2px'
                  }}></div>
                  <span style={{ fontWeight: '500' }}>{area.type}</span>
                </div>
                <span style={{ fontWeight: 'bold' }}>{area.percentage}%</span>
              </div>
              
              <div style={{
                width: '100%',
                height: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${area.percentage}%`,
                  height: '100%',
                  background: area.color,
                  transition: 'width 1s ease'
                }}></div>
              </div>
              
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                {area.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Feature Detection */}
      <div style={{ marginBottom: '2rem' }}>
        <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem' }}>
          Detected Features
        </h4>
        
        <div className="grid grid-2" style={{ gap: '1rem', fontSize: '0.875rem' }}>
          <div style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Cracks Detected</span>
              <span style={{ fontWeight: 'bold', color: 'var(--danger-color)' }}>
                {maskAnalysis.features.cracksDetected}
              </span>
            </div>
          </div>
          
          <div style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Unstable Slopes</span>
              <span style={{ fontWeight: 'bold', color: 'var(--warning-color)' }}>
                {maskAnalysis.features.unstableSlopes}
              </span>
            </div>
          </div>
          
          <div style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Vegetation Cover</span>
              <span style={{ fontWeight: 'bold', color: 'var(--success-color)' }}>
                {maskAnalysis.features.vegetationCover}%
              </span>
            </div>
          </div>
          
          <div style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Rock Exposure</span>
              <span style={{ fontWeight: 'bold', color: 'var(--info-color)' }}>
                {maskAnalysis.features.rockExposure}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Analysis Summary */}
      <div style={{
        padding: '1rem',
        background: 'rgba(255, 107, 53, 0.1)',
        border: '1px solid rgba(255, 107, 53, 0.3)',
        borderRadius: '8px'
      }}>
        <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--primary-color)' }}>
          AI Analysis Summary
        </h4>
        <p style={{ fontSize: '0.875rem', lineHeight: '1.4', margin: 0 }}>
          The AI model has identified significant risk areas covering {maskAnalysis.riskAreas[0].percentage}% of the analyzed region. 
          The presence of {maskAnalysis.features.cracksDetected} visible cracks and {maskAnalysis.features.unstableSlopes} unstable 
          slopes indicates elevated rockfall risk. Continuous monitoring is recommended for the highlighted high-risk zones.
        </p>
      </div>
    </div>
  )
}

export default MaskOverlay