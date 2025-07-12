import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Header from './components/Header'
import AvatarPage from './components/AvatarPage'
import AvatarSettings from './components/AvatarSettings'
import type { AvatarSettings as AvatarSettingsType } from './components/AvatarSettings'
import './App.css'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<AvatarPage />} />
            <Route path="/settings" element={<AvatarSettings onSettingsSaved={(settings) => console.log('Settings saved:', settings)} />} />
          </Routes>
        </main>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </div>
    </Router>
  )
}

export default App 