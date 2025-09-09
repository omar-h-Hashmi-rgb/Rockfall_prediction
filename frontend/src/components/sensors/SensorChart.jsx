import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

function SensorChart({ sensorData, timeRange }) {
  if (!sensorData) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        <p>Select a sensor to view data</p>
      </div>
    )
  }

  // Generate sample time series data based on timeRange
  const generateTimeLabels = () => {
    const labels = []
    const now = new Date()
    const intervalMinutes = timeRange <= 6 ? 15 : timeRange <= 24 ? 60 : 360
    const points = Math.min(50, (timeRange * 60) / intervalMinutes)
    
    for (let i = points - 1; i >= 0; i--) {
      const time = new Date(now.getTime() - i * intervalMinutes * 60000)
      labels.push(time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))
    }
    return labels
  }

  const generateDataPoints = (baseValue, variation = 0.1) => {
    const labels = generateTimeLabels()
    return labels.map((_, index) => {
      const trend = Math.sin(index * 0.1) * variation * baseValue
      const noise = (Math.random() - 0.5) * variation * baseValue
      return Math.max(0, baseValue + trend + noise)
    })
  }

  const labels = generateTimeLabels()
  
  const data = {
    labels,
    datasets: [
      {
        label: 'Displacement (mm)',
        data: generateDataPoints(2.4, 0.2),
        borderColor: 'rgb(255, 107, 53)',
        backgroundColor: 'rgba(255, 107, 53, 0.1)',
        yAxisID: 'y',
      },
      {
        label: 'Strain (μstrain)',
        data: generateDataPoints(125, 0.15),
        borderColor: 'rgb(247, 147, 30)',
        backgroundColor: 'rgba(247, 147, 30, 0.1)',
        yAxisID: 'y1',
      },
      {
        label: 'Pore Pressure (kPa)',
        data: generateDataPoints(215, 0.1),
        borderColor: 'rgb(52, 152, 219)',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        yAxisID: 'y2',
      },
      {
        label: 'Vibration (g)',
        data: generateDataPoints(0.08, 0.3),
        borderColor: 'rgb(39, 174, 96)',
        backgroundColor: 'rgba(39, 174, 96, 0.1)',
        yAxisID: 'y3',
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#ffffff',
          usePointStyle: true,
          padding: 20
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: '#b0b0b0'
        }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: '#b0b0b0'
        },
        title: {
          display: true,
          text: 'Displacement (mm)',
          color: '#ffffff'
        }
      },
      y1: {
        type: 'linear',
        display: false,
        position: 'right',
      },
      y2: {
        type: 'linear',
        display: false,
        position: 'right',
      },
      y3: {
        type: 'linear',
        display: false,
        position: 'right',
      }
    }
  }

  return (
    <div style={{ height: '400px' }}>
      <Line data={data} options={options} />
    </div>
  )
}

export default SensorChart