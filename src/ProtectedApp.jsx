import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './components/Login';
import TextToSpeech from './components/TextToSpeech';
import TextSummarization from './components/TextSummarization';
import LandingPage from './components/LandingPage';
import AudioTools from './components/AudioTools';
import ProtectedRoute from './components/ProtectedRoute';

function ProtectedApp() {
  const { authenticated, loading, login } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        fontSize: '20px',
        fontWeight: '600'
      }}>
        Loading...
      </div>
    );
  }

  if (!authenticated) {
    return <Login onLogin={login} />;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/tts" element={<TextToSpeech />} />
      <Route path="/summarize" element={<TextSummarization />} />
      <Route 
        path="/audio-tools" 
        element={
          <ProtectedRoute requiredRole="premium">
            <AudioTools />
          </ProtectedRoute>
        } 
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default ProtectedApp;



