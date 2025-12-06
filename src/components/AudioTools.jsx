import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { sendToNetSpeech, sendToSNR, sendToConverter } from '../api/audioService'
import './AudioTools.css'

function AudioTools() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileName, setFileName] = useState('');
  
  const [loadingNetSpeech, setLoadingNetSpeech] = useState(false);
  const [loadingSNR, setLoadingSNR] = useState(false);
  const [loadingConverter, setLoadingConverter] = useState(false);
  
  const [netSpeechResult, setNetSpeechResult] = useState(null);
  const [snrResult, setSnrResult] = useState(null);
  const [converterResult, setConverterResult] = useState(null);
  
  const [netSpeechError, setNetSpeechError] = useState(null);
  const [snrError, setSnrError] = useState(null);
  const [converterError, setConverterError] = useState(null);
  
  const [sampleRate, setSampleRate] = useState(22050);
  const [rate, setRate] = useState(1.0);
  const [returnType, setReturnType] = useState('url');
  const [audioFormat, setAudioFormat] = useState('wav');
  
  const handleBackToHome = () => navigate('/');
  
  const handleLogout = async () => {
    if (window.confirm('Bạn có chắc muốn đăng xuất?')) {
      await logout();
    }
  };
  
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setFileName(file.name);
      setNetSpeechResult(null);
      setSnrResult(null);
      setConverterResult(null);
      setNetSpeechError(null);
      setSnrError(null);
      setConverterError(null);
    }
  };
  
  const handleNetSpeechAnalysis = async () => {
    if (!selectedFile) {
      alert('Vui lòng chọn file audio trước');
      return;
    }
    
    setLoadingNetSpeech(true);
    setNetSpeechError(null);
    setNetSpeechResult(null);
    
    try {
      const result = await sendToNetSpeech(selectedFile);
      setNetSpeechResult(result);
    } catch (error) {
      setNetSpeechError(error.message);
    } finally {
      setLoadingNetSpeech(false);
    }
  };
  
  const handleSNRAnalysis = async () => {
    if (!selectedFile) {
      alert('Vui lòng chọn file audio trước');
      return;
    }
    
    setLoadingSNR(true);
    setSnrError(null);
    setSnrResult(null);
    
    try {
      const result = await sendToSNR(selectedFile);
      setSnrResult(result);
    } catch (error) {
      setSnrError(error.message);
    } finally {
      setLoadingSNR(false);
    }
  };
  
  const handleAudioConverter = async () => {
    if (!selectedFile) {
      alert('Vui lòng chọn file audio trước');
      return;
    }
    
    setLoadingConverter(true);
    setConverterError(null);
    setConverterResult(null);
    
    try {
      const params = { sample_rate: sampleRate, rate, return_type: returnType, audio_format: audioFormat };
      const result = await sendToConverter(selectedFile, params);
      setConverterResult(result);
    } catch (error) {
      setConverterError(error.message);
    } finally {
      setLoadingConverter(false);
    }
  };
  
  return (
    <div className="audio-tools-container">
      <header className="audio-tools-header">
        <div className="audio-tools-brand">
          <button onClick={handleBackToHome} className="audio-tools-back-btn">← Back</button>
          <span className="audio-tools-logo">🎵</span>
          <h1 className="audio-tools-title">Audio Tools</h1>
        </div>
        <div className="audio-tools-user">
          <span className="audio-tools-username">👤 {user?.email || user?.username}</span>
          <button onClick={handleLogout} className="audio-tools-logout-btn">Logout</button>
        </div>
      </header>
      
      <main className="audio-tools-main">
        <div className="audio-tools-upload">
          <h2>Upload Audio File</h2>
          <input type="file" id="audio-file" accept=".wav,.mp3,audio/*" onChange={handleFileChange} className="audio-tools-input" />
          <label htmlFor="audio-file" className="audio-tools-label">{fileName || 'Choose Audio File (.wav, .mp3)'}</label>
        </div>
        
        <div className="audio-tools-grid">
          <div className="audio-tools-section">
            <h3>🎤 NetSpeech</h3>
            <p>Detect human voice intervals</p>
            <button onClick={handleNetSpeechAnalysis} disabled={!selectedFile || loadingNetSpeech} className="audio-tools-btn">
              {loadingNetSpeech ? 'Analyzing...' : 'Analyze'}
            </button>
            {netSpeechError && <div className="audio-tools-error">❌ {netSpeechError}</div>}
            {netSpeechResult?.segments && (
              <div className="audio-tools-results">
                <h4>Voice Intervals:</h4>
                {netSpeechResult.segments.map((seg, i) => (
                  <div key={i} className="audio-tools-interval">
                    Segment {i + 1}: {seg[0].toFixed(2)}s - {seg[1].toFixed(2)}s
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="audio-tools-section">
            <h3>📊 SNR</h3>
            <p>Signal-to-Noise Ratio score</p>
            <button onClick={handleSNRAnalysis} disabled={!selectedFile || loadingSNR} className="audio-tools-btn">
              {loadingSNR ? 'Analyzing...' : 'Calculate SNR'}
            </button>
            {snrError && <div className="audio-tools-error">❌ {snrError}</div>}
            {snrResult?.snr && (
              <div className="audio-tools-results">
                <div className="audio-tools-snr-value">{snrResult.snr.toFixed(2)} dB</div>
                <div>{snrResult.snr >= 30 ? '✅ Excellent' : snrResult.snr >= 20 ? '✅ Good' : snrResult.snr >= 10 ? '⚠️ Fair' : '❌ Poor'}</div>
              </div>
            )}
          </div>
          
          <div className="audio-tools-section audio-tools-converter">
            <h3>🔄 Audio Converter</h3>
            <div className="audio-tools-params">
              <label>Sample Rate: <select value={sampleRate} onChange={(e) => setSampleRate(Number(e.target.value))} className="audio-tools-select">
                <option value={8000}>8000 Hz</option>
                <option value={16000}>16000 Hz</option>
                <option value={22050}>22050 Hz</option>
                <option value={44100}>44100 Hz</option>
                <option value={48000}>48000 Hz</option>
              </select></label>
              <label>Rate: <input type="number" min="0.5" max="2.0" step="0.1" value={rate} onChange={(e) => setRate(Number(e.target.value))} className="audio-tools-input-num" /></label>
              <label>Return: <select value={returnType} onChange={(e) => setReturnType(e.target.value)} className="audio-tools-select">
                <option value="url">URL</option>
                <option value="base64">Base64</option>
              </select></label>
              <label>Format: <select value={audioFormat} onChange={(e) => setAudioFormat(e.target.value)} className="audio-tools-select">
                <option value="wav">WAV</option>
                <option value="mp3">MP3</option>
              </select></label>
            </div>
            <button onClick={handleAudioConverter} disabled={!selectedFile || loadingConverter} className="audio-tools-btn">
              {loadingConverter ? 'Converting...' : 'Convert'}
            </button>
            {converterError && <div className="audio-tools-error">❌ {converterError}</div>}
            {converterResult?.audio && (
              <div className="audio-tools-results">
                <h4>Converted Audio:</h4>
                <audio controls src={converterResult.audio.startsWith('http') ? converterResult.audio : `data:audio/${audioFormat};base64,${converterResult.audio}`} />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default AudioTools;
