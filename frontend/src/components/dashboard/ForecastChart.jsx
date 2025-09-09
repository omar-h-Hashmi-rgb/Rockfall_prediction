import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

function ForecastChart({ predictions }) {
  // Generate forecast data based on recent predictions
  const generateForecastData = () => {
    const hours = Array.from({ length: 24 }, (_, i) => {
      const date = new Date()
      date.setHours(date.getHours() + i)
      return date.getHours().toString().padStart(2, '0') + ':00'
    })

    // Simulate forecast based on recent trends
    const riskData = hours.map((_, index) => {
      const baseRisk = predictions[0]?.risk_probability || 0.2
      const variation = Math.sin(index * 0.3) * 0.1 + Math.random() * 0.05
      return Math.max(0, Math.min(1, baseRisk + variation))
    })

    return { hours, riskData }
  }

  const { hours, riskData } = generateForecastData()

  const data = {
    labels: hours,
    datasets: [
      {
        label: 'Risk Probability',
        data: riskData,
        borderColor: 'rgb(255, 107, 53)',
        backgroundColor: 'rgba(255, 107, 53, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: riskData.map(risk => 
          risk > 0.7 ? '#e74c3c' : risk > 0.4 ? '#f39c12' : '#27ae60'
        ),
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#ffffff'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        callbacks: {
          label: function(context) {
            return `Risk: ${(context.parsed.y * 100).toFixed(1)}%`
          }
        }
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
        min: 0,
        max: 1,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: '#b0b0b0',
          callback: function(value) {
            return (value * 100).toFixed(0) + '%'
          }
        }
      }
    }
  }

  return (
    <div style={{ height: '300px' }}>
      <Line data={data} options={options} />
    </div>
  )
}

export default ForecastChart