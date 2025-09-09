import React from 'react'
import { ClerkProvider } from '@clerk/clerk-react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import SensorMonitoring from './pages/SensorMonitoring'
import ImageryAnalysis from './pages/ImageryAnalysis'
import Alerts from './pages/Alerts'
import Settings from './pages/Settings'

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || 'pk_test_demo_key'

function App() {
  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <BrowserRouter>
        <div className="App">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/sensors" element={<SensorMonitoring />} />
            <Route path="/imagery" element={<ImageryAnalysis />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ClerkProvider>
  )
}

export default App