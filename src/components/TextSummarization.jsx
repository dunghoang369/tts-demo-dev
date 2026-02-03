import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import TextEditor from './TextEditor'
import SettingsPanel from './SettingsPanel'
import NewsTags from './NewsTags'
import NewsNotification from './NewsNotification'
import { synthesize } from '../api/ttsService'
import { useNewsPolling } from '../hooks/useNewsPolling'
import { useAuth } from '../context/AuthContext'
import './TextSummarization.css'

function TextSummarization() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [voice, setVoice] = useState('4');
  const [model, setModel] = useState('');
  const [rate, setRate] = useState('1.0');
  const [returnType, setReturnType] = useState('url');
  const [audioFormat, setAudioFormat] = useState('wav');
  const [maxWordPerSent, setMaxWordPerSent] = useState(100);
  const [isLoading, setIsLoading] = useState(false);
  const [editorText, setEditorText] = useState('');

  // Use polling hook for auto-refresh news
  const { newsData, hasNewContent, isLoading: newsLoading, refreshNews } = useNewsPolling();

  const handleSynthesize = async (text) => {
    try {
      setIsLoading(true);
      const result = await synthesize(text, voice, model, rate, returnType, audioFormat, maxWordPerSent, true);
      
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

  const handleTagClick = (newsContent) => {
    setEditorText(newsContent);
  };

  return (
    <div className="text-summarization">
      <NewsNotification show={hasNewContent} onRefresh={refreshNews} />
      <header className="header">
        <div className="brand">
          <button onClick={handleBackToHome} className="back-button">
            ← Back
          </button>
          <span className="logo">📝</span>
          <h1 className="title">Collect and Summarize the news</h1>
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
            externalText={editorText}
            onTextChange={setEditorText}
            showSuggestions={false}
            readOnly={true}
          />
        </div>
        
        <aside className="news-tags-section">
          <NewsTags 
            newsData={Object.keys(newsData).length > 0 ? newsData : {}}
            onTagClick={handleTagClick}
          />
          {newsLoading && (
            <div style={{ padding: '10px', textAlign: 'center', fontSize: '12px', color: '#666' }}>
              Loading latest news...
            </div>
          )}
        </aside>
        
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

export default TextSummarization

