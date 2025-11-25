import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import ProtectedApp from './ProtectedApp.jsx'
import { AuthProvider } from './context/AuthContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <ProtectedApp />
    </AuthProvider>
  </StrictMode>,
)
