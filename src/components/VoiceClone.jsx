import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { generateVoiceClone } from '../api/audioService';
import RecordRTC from 'recordrtc';
import './VoiceClone.css';

function VoiceClone() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // Input mode state
  const [inputMode, setInputMode] = useState('upload'); // 'upload' or 'record'

  // Upload mode state
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileName, setFileName] = useState('');

  // Recording mode state
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [recordedAudioUrl, setRecordedAudioUrl] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const recorderRef = useRef(null);
  const streamRef = useRef(null);
  const recordingIntervalRef = useRef(null);
  const [sampleRate, setSampleRate] = useState(48000);

  // Common state
  const [refText, setRefText] = useState('');
  const [refLang, setRefLang] = useState('vi');
  const [genLang, setGenLang] = useState('vi');
  const [genText, setGenText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatedAudio, setGeneratedAudio] = useState(null);

  const handleBackToHome = () => navigate('/');

  const handleLogout = async () => {
    if (window.confirm('Bạn có chắc muốn đăng xuất?')) {
      await logout();
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Stop media stream tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      // Revoke audio URL
      if (recordedAudioUrl) {
        URL.revokeObjectURL(recordedAudioUrl);
      }
    };
  }, [recordedAudioUrl]);

  // Detect optimal sample rate
  useEffect(() => {
    const getSampleRate = async () => {
      try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const maxSampleRate = audioContext.sampleRate;
        setSampleRate(maxSampleRate);
        audioContext.close();
      } catch (error) {
        console.error("Error AudioContext:", error);
      }
    };
    getSampleRate();
  }, []);

  // Handle mode change
  const handleModeChange = (mode) => {
    setInputMode(mode);
    setError(null);
    setGeneratedAudio(null);
    
    // Clear opposite mode's data
    if (mode === 'upload') {
      // Switching to upload, clear recording
      clearRecording();
    } else {
      // Switching to record, clear upload
      setSelectedFile(null);
      setFileName('');
    }
  };

  // Recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { noiseSuppression: false, echoCancellation: false } 
      });
      streamRef.current = stream;

      recorderRef.current = new RecordRTC(stream, {
        type: 'audio',
        mimeType: 'audio/wav',
        sampleRate: sampleRate,
        numberOfAudioChannels: 2,
        recorderType: RecordRTC.StereoAudioRecorder,
      });

      recorderRef.current.startRecording();
      setIsRecording(true);
      setRecordingTime(0); // Reset timer
      setError(null);
      
      // Start timer interval
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prevTime => prevTime + 1);
      }, 1000);
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setError('Microphone access denied. Please allow microphone access to record.');
    }
  };

  const stopRecording = async () => {
    if (recorderRef.current && isRecording) {
      // Clear timer interval
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
      
      recorderRef.current.stopRecording(async () => {
        const audioBlob = recorderRef.current.getBlob();
        setRecordedBlob(audioBlob);
        
        const url = URL.createObjectURL(audioBlob);
        setRecordedAudioUrl(url);
        
        // Stop stream tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      });
      setIsRecording(false);
    }
  };

  const clearRecording = () => {
    if (recordedAudioUrl) {
      URL.revokeObjectURL(recordedAudioUrl);
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (recordingIntervalRef.current) {
      clearInterval(recordingIntervalRef.current);
    }
    setRecordedBlob(null);
    setRecordedAudioUrl(null);
    setRecordingTime(0);
    recorderRef.current = null;
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = time % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  };

  // Upload mode functions
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/x-wav'];
      if (!validTypes.includes(file.type) && !file.name.match(/\.(wav|mp3)$/i)) {
        setError('Please upload a valid audio file (.wav or .mp3)');
        return;
      }

      setSelectedFile(file);
      setFileName(file.name);
      setError(null);
      setGeneratedAudio(null);
    }
  };

  const handleGenerate = async () => {
    // Validation based on mode
    if (inputMode === 'upload' && !selectedFile) {
      setError('Please upload a reference audio file');
      return;
    }

    if (inputMode === 'record' && !recordedBlob) {
      setError('Please record your voice first');
      return;
    }

    if (!genText.trim()) {
      setError('Please enter text to generate');
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedAudio(null);

    try {
      // Determine which file to send
      let fileToSend;

      if (inputMode === 'upload') {
        fileToSend = selectedFile;
      } else {
        // Recording mode - always WAV format
        fileToSend = new File([recordedBlob], `recording_${Date.now()}.wav`, {
          type: 'audio/wav'
        });
        
        console.log('Converted blob to file:', fileToSend.name, 'type:', fileToSend.type);
      }

      const params = {
        gen_text: genText,
        ref_lang: refLang,
        gen_lang: genLang,
        ref_text: refText.trim() || null,
        is_upload: true,  // Always true for both modes
        is_translation: false,
      };

      console.log('Generating voice clone with params:', params);
      console.log('Input mode:', inputMode);

      const result = await generateVoiceClone(fileToSend, params);

      setGeneratedAudio(result);
      console.log('Voice clone generated successfully');
    } catch (err) {
      console.error('Voice clone error:', err);
      setError(err.message || 'Failed to generate voice clone');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setFileName('');
    clearRecording();
    setRefText('');
    setRefLang('vi');
    setGenLang('vi');
    setGenText('');
    setError(null);
    setGeneratedAudio(null);
  };

  const handleDownload = () => {
    if (generatedAudio && generatedAudio.blob) {
      const url = URL.createObjectURL(generatedAudio.blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `voice_clone_${Date.now()}.wav`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="voice-clone-container">
      <header className="voice-clone-header">
        <div className="voice-clone-header-left">
          <button className="voice-clone-back-button" onClick={handleBackToHome}>
            ← Back
          </button>
          <h1 className="voice-clone-title">🎤 Voice Clone</h1>
        </div>
        <div className="voice-clone-header-right">
          <span className="voice-clone-username">👤 {user?.email || user?.username}</span>
          <button onClick={handleLogout} className="voice-clone-logout-button">
            Logout
          </button>
        </div>
      </header>

      <main className="voice-clone-content">
        <div className="voice-clone-description">
          <p>
            Clone any voice by uploading a reference audio file or recording your voice directly.
            For best results, provide a clear reference audio and its transcript.
          </p>
        </div>

        <div className="voice-clone-form">
          {/* Input Mode Selector */}
          <div className="voice-clone-mode-selector">
            <label className="voice-clone-mode-option">
              <input
                type="radio"
                value="upload"
                checked={inputMode === 'upload'}
                onChange={(e) => handleModeChange(e.target.value)}
                disabled={loading}
              />
              <span>📁 Upload Audio</span>
            </label>
            <label className="voice-clone-mode-option">
              <input
                type="radio"
                value="record"
                checked={inputMode === 'record'}
                onChange={(e) => handleModeChange(e.target.value)}
                disabled={loading}
              />
              <span>🎤 Record Audio</span>
            </label>
          </div>

          {/* Reference Audio - Upload or Record */}
          <section className="voice-clone-section">
            <h3 className="voice-clone-section-title">1. Reference Audio *</h3>
            
            {inputMode === 'upload' ? (
              // Upload Mode
              <div className="voice-clone-upload-area">
                <input
                  type="file"
                  id="audio-file"
                  accept="audio/wav,audio/mp3,audio/mpeg"
                  onChange={handleFileChange}
                  className="voice-clone-file-input"
                  disabled={loading}
                />
                <label htmlFor="audio-file" className="voice-clone-file-label">
                  {fileName ? (
                    <>
                      <span className="voice-clone-file-icon">📁</span>
                      <span className="voice-clone-file-name">{fileName}</span>
                    </>
                  ) : (
                    <>
                      <span className="voice-clone-upload-icon">⬆️</span>
                      <span className="voice-clone-upload-text">
                        Click to upload reference audio
                      </span>
                      <span className="voice-clone-upload-hint">Supported: .wav, .mp3</span>
                    </>
                  )}
                </label>
              </div>
            ) : (
              // Record Mode
              <div className="voice-clone-recording-section">
                {/* Sample sentence instruction */}
                <div className="voice-clone-sample-instruction">
                  <p className="voice-clone-instruction-text">
                    Đọc câu sau trong khoảng 8 - 10 giây:
                  </p>
                  <div className="voice-clone-sample-text">
                    Namibank xin kính chào quý khách, Cảm ơn quý khách đã gọi đến tổng đài chăm sóc khách 
                    hàng của ngân hàng Nami. Em có thể hỗ trợ thông tin gì cho quý khách ạ?
                  </div>
                </div>
                
                <div className="voice-clone-recording-controls">
                  {!isRecording && !recordedBlob && (
                    <button
                      className="voice-clone-record-button"
                      onClick={startRecording}
                      disabled={loading}
                    >
                      🎤 Start Recording
                    </button>
                  )}
                  
                  {isRecording && (
                    <>
                      <button
                        className="voice-clone-record-button recording"
                        onClick={stopRecording}
                      >
                        ⏹️ Stop Recording
                      </button>
                      <div className="voice-clone-recording-timer">
                        Duration: {formatTime(recordingTime)}
                      </div>
                    </>
                  )}
                  
                  {recordedBlob && !isRecording && (
                    <button
                      className="voice-clone-rerecord-button"
                      onClick={clearRecording}
                      disabled={loading}
                    >
                      🔄 Re-record
                    </button>
                  )}
                </div>
                
                {recordedBlob && recordedAudioUrl && (
                  <div className="voice-clone-preview-section">
                    <p className="voice-clone-preview-label">Preview your recording:</p>
                    <audio
                      controls
                      src={recordedAudioUrl}
                      className="voice-clone-preview-player"
                      preload="metadata"
                    >
                      Your browser does not support the audio element.
                    </audio>
                  </div>
                )}
              </div>
            )}
          </section>

          {/* Reference Text (Optional) */}
          <section className="voice-clone-section">
            <h3 className="voice-clone-section-title">
              2. Reference Text (Optional)
              <span className="voice-clone-hint">Improves generation quality</span>
            </h3>
            <textarea
              className="voice-clone-textarea"
              placeholder="Enter the transcript of your reference audio here (optional, but recommended for better quality)..."
              value={refText}
              onChange={(e) => setRefText(e.target.value)}
              rows={3}
            />
          </section>

          {/* Language Selection */}
          <section className="voice-clone-section">
            <h3 className="voice-clone-section-title">3. Language Settings *</h3>
            <div className="voice-clone-language-grid">
              <div className="voice-clone-input-group">
                <label className="voice-clone-label">Reference Language:</label>
                <select
                  className="voice-clone-select"
                  value={refLang}
                  onChange={(e) => setRefLang(e.target.value)}
                >
                  <option value="vi">🇻🇳 Vietnamese</option>
                  <option value="en">🇺🇸 English</option>
                  <option value="ja">🇯🇵 Japanese</option>
                </select>
              </div>

              <div className="voice-clone-input-group">
                <label className="voice-clone-label">Generation Language:</label>
                <select
                  className="voice-clone-select"
                  value={genLang}
                  onChange={(e) => setGenLang(e.target.value)}
                >
                  <option value="vi">🇻🇳 Vietnamese</option>
                  <option value="en">🇺🇸 English</option>
                  <option value="ja">🇯🇵 Japanese</option>
                </select>
              </div>
            </div>
          </section>

          {/* Generation Text */}
          <section className="voice-clone-section">
            <h3 className="voice-clone-section-title">4. Text to Generate *</h3>
            <textarea
              className="voice-clone-textarea voice-clone-textarea-large"
              placeholder="Enter the text you want to generate with the cloned voice..."
              value={genText}
              onChange={(e) => setGenText(e.target.value)}
              rows={5}
            />
          </section>

          {/* Action Buttons */}
          <div className="voice-clone-actions">
            <button
              className="voice-clone-button voice-clone-button-primary"
              onClick={handleGenerate}
              disabled={
                loading || 
                (inputMode === 'upload' && !selectedFile) ||
                (inputMode === 'record' && !recordedBlob) ||
                !genText.trim()
              }
            >
              {loading ? (
                <>
                  <span className="voice-clone-spinner"></span>
                  Generating...
                </>
              ) : (
                <>🎙️ Generate Voice Clone</>
              )}
            </button>

            <button
              className="voice-clone-button voice-clone-button-secondary"
              onClick={handleClear}
              disabled={loading}
            >
              🔄 Clear All
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="voice-clone-error">
              <span className="voice-clone-error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Generated Audio */}
          {generatedAudio && (
            <section className="voice-clone-section voice-clone-result">
              <h3 className="voice-clone-section-title">✅ Generated Audio</h3>
              <div className="voice-clone-audio-container">
                <audio
                  controls
                  src={generatedAudio.audioUrl}
                  className="voice-clone-audio-player"
                  key={generatedAudio.audioUrl}
                  preload="metadata"
                >
                  Your browser does not support the audio element.
                </audio>
                <button
                  className="voice-clone-button voice-clone-button-download"
                  onClick={handleDownload}
                >
                  💾 Download Audio
                </button>
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

export default VoiceClone;








