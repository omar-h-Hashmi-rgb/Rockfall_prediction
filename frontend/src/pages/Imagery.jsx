import React, { useState, useEffect } from 'react'
import { Camera, Eye, Grid, Download } from 'lucide-react'
import ImageViewer from '../components/imagery/ImageViewer'
import MaskOverlay from '../components/imagery/MaskOverlay'

function Imagery() {
  const [selectedImage, setSelectedImage] = useState(null)
  const [viewMode, setViewMode] = useState('grid')
  const [showMasks, setShowMasks] = useState(false)
  const [images, setImages] = useState([])

  useEffect(() => {
    // Generate sample image data (in real app, fetch from API)
    generateSampleImages()
  }, [])

  const generateSampleImages = () => {
    const sampleImages = Array.from({ length: 12 }, (_, index) => ({
      id: index + 1,
      name: `drone_image_${(index + 1).toString().padStart(3, '0')}.jpg`,
      timestamp: new Date(Date.now() - index * 3600000).toISOString(),
      sector: `Sector ${Math.floor(index / 3) + 1}`,
      riskLevel: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)],
      thumbnail: `https://picsum.photos/300/200?random=${index}`,
      fullSize: `https://picsum.photos/800/600?random=${index}`,
      maskAvailable: Math.random() > 0.3
    }))
    setImages(sampleImages)
  }

  const handleImageSelect = (image) => {
    setSelectedImage(image)
  }

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'High': return 'var(--danger-color)'
      case 'Medium': return 'var(--warning-color)'
      case 'Low': return 'var(--success-color)'
      default: return 'var(--text-muted)'
    }
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Drone Imagery Analysis
        </h1>
        <p className="text-secondary">
          View and analyze drone-captured images with AI-generated risk masks
        </p>
      </div>

      {/* Controls */}
      <div className="card mb-4">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button
              onClick={() => setViewMode('grid')}
              className={`btn ${viewMode === 'grid' ? 'btn-primary' : ''}`}
              style={{
                background: viewMode === 'grid' ? 'var(--primary-color)' : 'transparent',
                border: '1px solid var(--border-color)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <Grid size={16} />
              Grid View
            </button>
            
            <button
              onClick={() => setViewMode('detailed')}
              className={`btn ${viewMode === 'detailed' ? 'btn-primary' : ''}`}
              style={{
                background: viewMode === 'detailed' ? 'var(--primary-color)' : 'transparent',
                border: '1px solid var(--border-color)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <Eye size={16} />
              Detailed View
            </button>
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={showMasks}
                onChange={(e) => setShowMasks(e.target.checked)}
              />
              Show Risk Masks
            </label>
            
            <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Download size={16} />
              Export Data
            </button>
          </div>
        </div>
      </div>

      {/* Image Grid */}
      {viewMode === 'grid' && (
        <div className="grid grid-4">
          {images.map((image) => (
            <div
              key={image.id}
              className="card"
              style={{ 
                cursor: 'pointer',
                transition: 'transform 0.3s ease',
                ':hover': { transform: 'translateY(-4px)' }
              }}
              onClick={() => handleImageSelect(image)}
            >
              <div style={{ position: 'relative', marginBottom: '1rem' }}>
                <img
                  src={image.thumbnail}
                  alt={image.name}
                  style={{
                    width: '100%',
                    height: '150px',
                    objectFit: 'cover',
                    borderRadius: '8px'
                  }}
                />
                
                {showMasks && image.maskAvailable && (
                  <div style={{
                    position: 'absolute',
                    top: '8px',
                    right: '8px',
                    background: 'rgba(0, 0, 0, 0.7)',
                    color: 'white',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.75rem'
                  }}>
                    MASK
                  </div>
                )}
                
                <div style={{
                  position: 'absolute',
                  top: '8px',
                  left: '8px',
                  background: getRiskColor(image.riskLevel),
                  color: 'white',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: 'bold'
                }}>
                  {image.riskLevel}
                </div>
              </div>
              
              <h4 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                {image.name}
              </h4>
              
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                <p>{image.sector}</p>
                <p>{new Date(image.timestamp).toLocaleString()}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detailed View */}
      {viewMode === 'detailed' && selectedImage && (
        <div className="grid grid-2" style={{ gap: '2rem' }}>
          <ImageViewer image={selectedImage} showMasks={showMasks} />
          {showMasks && selectedImage.maskAvailable && (
            <MaskOverlay image={selectedImage} />
          )}
        </div>
      )}

      {/* Image List for Selection */}
      {viewMode === 'detailed' && (
        <div className="card mt-4">
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            Select Image
          </h3>
          <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', padding: '0.5rem 0' }}>
            {images.map((image) => (
              <div
                key={image.id}
                onClick={() => handleImageSelect(image)}
                style={{
                  minWidth: '100px',
                  height: '75px',
                  cursor: 'pointer',
                  border: selectedImage?.id === image.id ? '2px solid var(--primary-color)' : '1px solid var(--border-color)',
                  borderRadius: '4px',
                  overflow: 'hidden'
                }}
              >
                <img
                  src={image.thumbnail}
                  alt={image.name}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover'
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Imagery