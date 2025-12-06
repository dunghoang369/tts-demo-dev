import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { sendToNetSpeech, sendToSNR, sendToConverter } from '../api/audioService'
import './AudioTools.css'

function AudioTools() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  
  // File state
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileName, setFileName] = useState('');
  
  // Loading states for each API
  const [loadingNetSpeech, setLoadingNetSpeech] = useState(false);
  const [loadingSNR, setLoadingSNR] = useState(false);
  const [loadingConverter, setLoadingConverter] = useState(false);
  
  // Results for each API
  const [netSpeechResult, setNetSpeechResult] = useState(null);
  const [snrResult, setSnrResult] = useState(null);
  const [converterResult, setConverterResult] = useState(null);
  
  // Error states
  const [netSpeechError, setNetSpeechError] = useState(null);
  const [snrError, setSnrError] = useState(null);
  const [converterError, setConverterError] = useState(null);
  
  // Audio Converter parameters
  const [sampleRate, setSampleRate] = useState(22050);
  const [rate, setRate] = useState(1.0);
  const [returnType, setReturnType] = useState('url');
  const [audioFormat, setAudioFormat] = useState('wav');
  
  const handleBackToHome = () => {
    navigate('/');
  };
  
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
      // Clear previous results when new file is selected
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
      const params = {
        sample_rate: sampleRate,
        rate: rate,
        return_type: returnType,
        audio_format: audioFormat
      };
      const result = await sendToConverter(selectedFile, params);
      setConverterResult(result);
    } catch (error) {
      setConverterError(error.message);
    } finally {
      setLoadingConverter(false);
    }
  };
  
  return (
    <div className="audio-tools">
      <header className="header">
        <div className="brand">
          <button onClick={handleBackToHome} className="back-button">
            ← Back
          </button>
          <span className="logo">🎵</span>
          <h1 className="title">Audio Tools</h1>
        </div>
        <div className="user-section">
          <span className="username">👤 {user?.email || user?.username}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>
      
      <main className="audio-tools-main">
        <div className="file-upload-section">
          <h2>Upload Audio File</h2>
          <div className="file-upload-container">
            <input
              type="file"
              id="audio-file"
              accept=".wav,.mp3,audio/*"
              onChange={handleFileChange}
              className="file-input"
            />
            <label htmlFor="audio-file" className="file-label">
              {fileName || 'Choose Audio File (.wav, .mp3)'}
            </label>
          </div>
        </div>
        
        <div className="api-sections">
          {/* NetSpeech Quality Analysis */}
          <div className="api-section">
            <h3>🎤 NetSpeech Quality Analysis</h3>
            <p className="api-description">
              Detect intervals of time that contain human voice in the audio
            </p>
            <button
              onClick={handleNetSpeechAnalysis}
              disabled={!selectedFile || loadingNetSpeech}
              className="api-button"
            >
              {loadingNetSpeech ? 'Analyzing...' : 'Analyze Quality'}
            </button>
            
            {netSpeechError && (
              <div className="error-message">
                ❌ Error: {netSpeechError}
              </div>
            )}
            
            {netSpeechResult && (
              <div className="result-container">
                <h4>Voice Activity Intervals:</h4>
                {netSpeechResult.segments && netSpeechResult.segments.length > 0 ? (
                  <div className="intervals-list">
                    {netSpeechResult.segments.map((segment, index) => (
                      <div key={index} className="interval-item">
                        <span className="interval-label">Segment {index + 1}:</span>
                        <span className="interval-time">
                          {segment[0].toFixed(2)}s - {segment[1].toFixed(2)}s
                        </span>
                        <span className="interval-duration">
                          (Duration: {(segment[1] - segment[0]).toFixed(2)}s)
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-result">No voice detected in audio</p>
                )}
              </div>
            )}
          </div>
          
          {/* SNR Analysis */}
          <div className="api-section">
            <h3>📊 SNR Analysis</h3>
            <p className="api-description">
              Calculate Signal-to-Noise Ratio score for audio quality assessment
            </p>
            <button
              onClick={handleSNRAnalysis}
              disabled={!selectedFile || loadingSNR}
              className="api-button"
            >
              {loadingSNR ? 'Analyzing...' : 'Calculate SNR'}
            </button>
            
            {snrError && (
              <div className="error-message">
                ❌ Error: {snrError}
              </div>
            )}
            
            {snrResult && (
              <div className="result-container">
                <h4>Signal-to-Noise Ratio:</h4>
                <div className="snr-result">
                  <div className="snr-value">
                    {snrResult.snr ? snrResult.snr.toFixed(2) : 'N/A'} dB
                  </div>
                  <div className="snr-quality">
                    {snrResult.snr >= 30 ? '✅ Excellent Quality' : 
                     snrResult.snr >= 20 ? '✅ Good Quality' :
                     snrResult.snr >= 10 ? '⚠️ Fair Quality' :
                     '❌ Poor Quality'}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Audio Converter */}
          <div className="api-section converter-section">
            <h3>🔄 Audio Converter</h3>
            <p className="api-description">
              Convert audio with custom parameters
            </p>
            
            <div className="converter-params">
              <div className="param-group">
                <label>Sample Rate:</label>
                <select
                  value={sampleRate}
                  onChange={(e) => setSampleRate(Number(e.target.value))}
                  className="param-select"
                >
                  <option value={8000}>8000 Hz</option>
                  <option value={16000}>16000 Hz</option>
                  <option value={22050}>22050 Hz</option>
                  <option value={44100}>44100 Hz</option>
                  <option value={48000}>48000 Hz</option>
                </select>
              </div>
              
              <div className="param-group">
                <label>Playback Rate:</label>
                <input
                  type="number"
                  min="0.5"
                  max="2.0"
                  step="0.1"
                  value={rate}
                  onChange={(e) => setRate(Number(e.target.value))}
                  className="param-input"
                />
              </div>
              
              <div className="param-group">
                <label>Return Type:</label>
                <select
                  value={returnType}
                  onChange={(e) => setReturnType(e.target.value)}
                  className="param-select"
                >
                  <option value="url">URL</option>
                  <option value="base64">Base64</option>
                </select>
              </div>
              
              <div className="param-group">
                <label>Audio Format:</label>
                <select
                  value={audioFormat}
                  onChange={(e) => setAudioFormat(e.target.value)}
                  className="param-select"
                >
                  <option value="wav">WAV</option>
                  <option value="mp3">MP3</option>
                </select>
              </div>
            </div>
            
            <button
              onClick={handleAudioConverter}
              disabled={!selectedFile || loadingConverter}
              className="api-button"
            >
              {loadingConverter ? 'Converting...' : 'Convert Audio'}
            </button>
            
            {converterError && (
              <div className="error-message">
                ❌ Error: {converterError}
              </div>
            )}
            
            {converterResult && (
              <div className="result-container">
                <h4>Results:</h4>
                <pre className="result-json">
                  {JSON.stringify(converterResult, null, 2)}
                </pre>
                {converterResult.audio && returnType === 'url' && (
                  <div className="audio-player">
                    <h5>Converted Audio:</h5>
                    <audio controls src={converterResult.audio}>
                      Your browser does not support the audio element.
                    </audio>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default AudioTools;

