import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import TextEditor from './TextEditor'
import SettingsPanel from './SettingsPanel'
import TextNorm from './TextNorm'
import { synthesize } from '../api/ttsService'
import { useAuth } from '../context/AuthContext'
import './TextToSpeech.css'

function TextToSpeech() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [voice, setVoice] = useState('4');
  const [model, setModel] = useState('');
  const [rate, setRate] = useState('1.0');
  const [returnType, setReturnType] = useState('url');
  const [audioFormat, setAudioFormat] = useState('wav');
  const [maxWordPerSent, setMaxWordPerSent] = useState(100);
  const [normalizedText, setNormalizedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSynthesize = async (text) => {
    try {
      setIsLoading(true);
      console.log('Starting TTS synthesis...');
      const result = await synthesize(text, voice, model, rate, returnType, audioFormat, maxWordPerSent, false);
      
      console.log('TTS Result:', result);
      console.log('Normalized Text from result:', result.normalizedText);
      
      // Extract normalized text from response
      if (result.normalizedText) {
        console.log('Setting normalized text:', result.normalizedText);
        setNormalizedText(result.normalizedText);
      } else {
        console.warn('No normalized text in response');
        setNormalizedText('');
      }
      
      return result.audioUrl;
    } catch (error) {
      console.error('Synthesis failed:', error);
      alert('Không thể tạo giọng nói. Vui lòng thử lại.');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    if (window.confirm('Bạn có chắc muốn đăng xuất?')) {
      await logout();
    }
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  return (
    <div className="text-to-speech">
      <header className="header">
        <div className="brand">
          <button onClick={handleBackToHome} className="back-button">
            ← Back
          </button>
          <span className="logo">🔊</span>
          <h1 className="title">Text to Speech</h1>
        </div>
        <div className="user-section">
          <span className="username">👤 {user?.email || user?.username}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>

      <main className="main-layout">
        <div className="editor-section">
          <TextEditor 
            onSynthesize={handleSynthesize}
            isLoading={isLoading}
          />
          <TextNorm normalizedText={normalizedText} />
        </div>
        
        <aside className="settings-section">
          <SettingsPanel 
            voice={voice}
            setVoice={setVoice}
            model={model}
            setModel={setModel}
            rate={rate}
            setRate={setRate}
            returnType={returnType}
            setReturnType={setReturnType}
            audioFormat={audioFormat}
            setAudioFormat={setAudioFormat}
            maxWordPerSent={maxWordPerSent}
            setMaxWordPerSent={setMaxWordPerSent}
          />
        </aside>
      </main>
    </div>
  )
}

export default TextToSpeech

