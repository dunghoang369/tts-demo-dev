import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './LandingPage.css';

function LandingPage() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      await logout();
    }
  };

  return (
    <div className="landing-page">
      <header className="landing-header">
        <div className="brand">
          <span className="logo">🔊</span>
          <h1 className="title">Text to Speech Platform</h1>
        </div>
        <div className="user-section">
          <span className="username">👤 {user?.email || user?.username}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>

      <main className="landing-content">
        <div className="welcome-section">
          <h2 className="welcome-title">Welcome to TTS Platform</h2>
          <p className="welcome-subtitle">
            Choose a service to get started
          </p>
        </div>

        <div className="services-grid">
          <Link to="/tts" className="service-card">
            <div className="service-icon">🎙️</div>
            <h3 className="service-title">Text to Speech</h3>
            <p className="service-description">
              Convert your text into natural-sounding speech with advanced voice synthesis
            </p>
            <div className="service-button">
              Get Started →
            </div>
          </Link>

          <Link to="/summarize" className="service-card">
            <div className="service-icon">📝</div>
            <h3 className="service-title">Text Summarization</h3>
            <p className="service-description">
              Summarize long texts and convert them to speech in one seamless workflow
            </p>
            <div className="service-button">
              Get Started →
            </div>
          </Link>

          <Link to="/audio-tools" className="service-card">
            <div className="service-icon">🎵</div>
            <h3 className="service-title">Audio Tools</h3>
            <p className="service-description">
              Detect voice activity, calculate SNR score, and convert audio formats
            </p>
            <div className="service-button">
              Get Started →
            </div>
          </Link>
        </div>

        <div className="features-section">
          <h3 className="features-title">Key Features</h3>
          <div className="features-list">
            <div className="feature-item">
              <span className="feature-icon">⚡</span>
              <span>Fast & Reliable</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🎯</span>
              <span>High Quality Voice</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🔄</span>
              <span>Real-time Processing</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📰</span>
              <span>News Integration</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default LandingPage;


