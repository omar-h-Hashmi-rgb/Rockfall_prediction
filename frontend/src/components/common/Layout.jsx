import React from 'react'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

function Layout({ children }) {
  return (
    <div className="mining-theme">
      <Navbar />
      <div style={{ display: 'flex', minHeight: 'calc(100vh - 70px)' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '2rem', overflow: 'auto' }}>
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout