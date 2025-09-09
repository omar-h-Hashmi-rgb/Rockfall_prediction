import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { SignedIn, SignedOut } from '@clerk/clerk-react'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import Imagery from './pages/Imagery'
import Sensors from './pages/Sensors'
import Settings from './pages/Settings'
import Layout from './components/common/Layout'

function Router() {
  return (
    <Routes>
      <Route 
        path="/login" 
        element={
          <SignedOut>
            <Login />
          </SignedOut>
        } 
      />
      
      <Route 
        path="/*" 
        element={
          <SignedIn>
            <Layout>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/alerts" element={<Alerts />} />
                <Route path="/imagery" element={<Imagery />} />
                <Route path="/sensors" element={<Sensors />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Layout>
          </SignedIn>
        } 
      />
      
      <Route 
        path="*" 
        element={
          <>
            <SignedOut>
              <Navigate to="/login" replace />
            </SignedOut>
            <SignedIn>
              <Navigate to="/dashboard" replace />
            </SignedIn>
          </>
        } 
      />
    </Routes>
  )
}

export default Router