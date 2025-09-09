import React, { useState } from 'react'
import { ZoomIn, ZoomOut, RotateCw, Download, Info } from 'lucide-react'

function ImageViewer({ image, showMasks }) {
  const [zoom, setZoom] = useState(1)
  const [rotation, setRotation] = useState(0)

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.25, 3))
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.25, 0.5))
  const handleRotate = () => setRotation(prev => (prev + 90) % 360)

  if (!image) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <Info size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
        <p className="text-muted">Select an image to view</p>
      </div>
    )
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600' }}>
          {image.name}
        </h3>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={handleZoomOut} className="btn" style={{ padding: '0.5rem' }}>
            <ZoomOut size={16} />
          </button>
          <button onClick={handleZoomIn} className="btn" style={{ padding: '0.5rem' }}>
            <ZoomIn size={16} />
          </button>
          <button onClick={handleRotate} className="btn" style={{ padding: '0.5rem' }}>
            <RotateCw size={16} />
          </button>
          <button className="btn btn-primary" style={{ padding: '0.5rem' }}>
            <Download size={16} />
          </button>
        </div>
      </div>

      <div style={{
        position: 'relative',
        overflow: 'hidden',
        borderRadius: '8px',
        background: '#000',
        height: '400px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <img
          src={image.fullSize}
          alt={image.name}
          style={{
            maxWidth: '100%',
            maxHeight: '100%',
            transform: `scale(${zoom}) rotate(${rotation}deg)`,
            transition: 'transform 0.3s ease',
            objectFit: 'contain'
          }}
        />
        
        {showMasks && image.maskAvailable && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `linear-gradient(45deg, 
              transparent 30%, 
              rgba(255, 0, 0, 0.2) 40%, 
              transparent 50%,
              rgba(255, 255, 0, 0.2) 60%,
              transparent 70%
            )`,
            pointerEvents: 'none'
          }} />
        )}
      </div>

      <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px' }}>
        <div className="grid grid-2" style={{ gap: '1rem', fontSize: '0.875rem' }}>
          <div>
            <strong>Sector:</strong> {image.sector}
          </div>
          <div>
            <strong>Risk Level:</strong> 
            <span style={{ 
              color: image.riskLevel === 'High' ? 'var(--danger-color)' : 
                     image.riskLevel === 'Medium' ? 'var(--warning-color)' : 'var(--success-color)',
              marginLeft: '0.5rem',
              fontWeight: 'bold'
            }}>
              {image.riskLevel}
            </span>
          </div>
          <div>
            <strong>Captured:</strong> {new Date(image.timestamp).toLocaleString()}
          </div>
          <div>
            <strong>Mask Available:</strong> {image.maskAvailable ? 'Yes' : 'No'}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ImageViewer