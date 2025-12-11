import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { generateVoiceClone } from '../api/audioService';
import './VoiceClone.css';

function VoiceClone() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [selectedFile, setSelectedFile] = useState(null);
  const [fileName, setFileName] = useState('');
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
    // Validation
    if (!selectedFile) {
      setError('Please upload a reference audio file');
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
      const params = {
        gen_text: genText,
        ref_lang: refLang,
        gen_lang: genLang,
        ref_text: refText.trim() || null,
        is_upload: true,
        is_translation: false,
      };

      console.log('Generating voice clone with params:', params);

      const result = await generateVoiceClone(selectedFile, params);

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
            Clone any voice by uploading a reference audio file and generate speech with that voice.
            For best results, provide a clear reference audio and its transcript.
          </p>
        </div>

        <div className="voice-clone-form">
          {/* Reference Audio Upload */}
          <section className="voice-clone-section">
            <h3 className="voice-clone-section-title">1. Reference Audio *</h3>
            <div className="voice-clone-upload-area">
              <input
                type="file"
                id="audio-file"
                accept="audio/wav,audio/mp3,audio/mpeg"
                onChange={handleFileChange}
                className="voice-clone-file-input"
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
              disabled={loading || !selectedFile || !genText.trim()}
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






