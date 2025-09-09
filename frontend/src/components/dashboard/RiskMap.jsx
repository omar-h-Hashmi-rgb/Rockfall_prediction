import React, { useEffect, useRef } from 'react'
import { MapPin } from 'lucide-react'

function RiskMap({ predictions }) {
  const mapRef = useRef(null)

  useEffect(() => {
    // Initialize basic map visualization
    if (mapRef.current) {
      // This would integrate with MapMyIndia API in production
      renderMap()
    }
  }, [predictions])

  const renderMap = () => {
    const canvas = mapRef.current
    const ctx = canvas.getContext('2d')
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Draw background (mine terrain)
    ctx.fillStyle = '#2d2d2d'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    // Draw grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
    ctx.lineWidth = 1
    for (let i = 0; i < canvas.width; i += 50) {
      ctx.beginPath()
      ctx.moveTo(i, 0)
      ctx.lineTo(i, canvas.height)
      ctx.stroke()
    }
    for (let i = 0; i < canvas.height; i += 50) {
      ctx.beginPath()
      ctx.moveTo(0, i)
      ctx.lineTo(canvas.width, i)
      ctx.stroke()
    }
    
    // Draw risk points
    predictions.forEach((prediction, index) => {
      const x = 50 + (index * 80) % (canvas.width - 100)
      const y = 50 + Math.floor(index / 4) * 80
      
      const color = prediction.risk_class === 'High' ? '#e74c3c' :
                   prediction.risk_class === 'Medium' ? '#f39c12' : '#27ae60'
      
      // Draw risk circle
      ctx.beginPath()
      ctx.arc(x, y, 15, 0, 2 * Math.PI)
      ctx.fillStyle = color
      ctx.fill()
      
      // Draw outer ring for high risk
      if (prediction.risk_class === 'High') {
        ctx.beginPath()
        ctx.arc(x, y, 25, 0, 2 * Math.PI)
        ctx.strokeStyle = color
        ctx.lineWidth = 2
        ctx.stroke()
      }
      
      // Draw probability text
      ctx.fillStyle = 'white'
      ctx.font = '10px Arial'
      ctx.textAlign = 'center'
      ctx.fillText(`${(prediction.risk_probability * 100).toFixed(0)}%`, x, y + 3)
    })
  }

  return (
    <div style={{ position: 'relative' }}>
      <canvas 
        ref={mapRef}
        width={400}
        height={300}
        style={{ 
          width: '100%', 
          height: '300px',
          border: '1px solid var(--border-color)',
          borderRadius: '8px'
        }}
      />
      
      <div style={{
        position: 'absolute',
        bottom: '10px',
        left: '10px',
        background: 'rgba(0, 0, 0, 0.7)',
        padding: '0.5rem',
        borderRadius: '4px',
        fontSize: '0.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <div style={{ width: '12px', height: '12px', background: '#e74c3c', borderRadius: '50%' }}></div>
          High Risk
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <div style={{ width: '12px', height: '12px', background: '#f39c12', borderRadius: '50%' }}></div>
          Medium Risk
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: '12px', height: '12px', background: '#27ae60', borderRadius: '50%' }}></div>
          Low Risk
        </div>
      </div>
    </div>
  )
}

export default RiskMap