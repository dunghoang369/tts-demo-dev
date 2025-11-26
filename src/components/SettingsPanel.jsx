import { useState, useEffect } from 'react';
import { getVoices, getModels, getRates, getReturnTypes, getAudioFormats } from '../api/ttsService';
import './SettingsPanel.css';

function SettingsPanel({ 
  voice, 
  setVoice, 
  model, 
  setModel,
  rate,
  setRate,
  returnType,
  setReturnType,
  audioFormat,
  setAudioFormat,
  maxWordPerSent,
  setMaxWordPerSent
}) {
  const [voices, setVoices] = useState([]);
  const [models, setModels] = useState([]);
  const [rates, setRates] = useState([]);
  const [returnTypes, setReturnTypes] = useState([]);
  const [audioFormats, setAudioFormats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVoicesAndModels();
  }, []);

  const loadVoicesAndModels = async () => {
    try {
      setLoading(true);
      const [voicesData, modelsData, ratesData, returnTypesData, audioFormatsData] = await Promise.all([
        getVoices(),
        getModels(),
        getRates(),
        getReturnTypes(),
        getAudioFormats()
      ]);
      
      setVoices(voicesData);
      setModels(modelsData);
      setRates(ratesData);
      setReturnTypes(returnTypesData);
      setAudioFormats(audioFormatsData);
      
      // Set default selections
      if (voicesData.length > 0 && !voice) {
        setVoice('4');  // Hồng Phượng (Nữ miền Bắc - Vi)
      }
      if (modelsData.length > 0 && !model) {
        setModel('22050');
      }
      if (ratesData.length > 0 && !rate) {
        setRate('1.0');
      }
      if (returnTypesData.length > 0 && !returnType) {
        setReturnType('url');
      }
      if (audioFormatsData.length > 0 && !audioFormat) {
        setAudioFormat('wav');
      }
    } catch (error) {
      console.error('Failed to load voices and models:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="settings-panel">
      <div className="settings-content">
        {/* Voice Selection */}
        <div className="setting-group">
          <label className="setting-label">Voice</label>
          {loading ? (
            <div className="loading-placeholder">Loading voices...</div>
          ) : (
            <select
              id="voice-select"
              className="setting-select"
              value={voice}
              onChange={(e) => setVoice(e.target.value)}
            >
              {voices.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Model Selection */}
        <div className="setting-group">
          <label className="setting-label">Model</label>
          {loading ? (
            <div className="loading-placeholder">Loading models...</div>
          ) : (
            <select
              id="model-select"
              className="setting-select"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              {models.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Rate Selection */}
        <div className="setting-group">
          <label className="setting-label">Speed</label>
          {loading ? (
            <div className="loading-placeholder">Loading rates...</div>
          ) : (
            <select
              id="rate-select"
              className="setting-select"
              value={rate}
              onChange={(e) => setRate(e.target.value)}
            >
              {rates.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Audio Format Selection */}
        <div className="setting-group">
          <label className="setting-label">Audio Format</label>
          {loading ? (
            <div className="loading-placeholder">Loading...</div>
          ) : (
            <select
              id="audioformat-select"
              className="setting-select"
              value={audioFormat}
              onChange={(e) => setAudioFormat(e.target.value)}
            >
              {audioFormats.map((af) => (
                <option key={af.id} value={af.id}>
                  {af.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Max Words Per Sentence Slider */}
        <div className="setting-group">
          <label className="setting-label">
            Max Words Per Sentence: {maxWordPerSent}
          </label>
          <input
            type="range"
            id="max-word-slider"
            className="setting-slider"
            min="10"
            max="500"
            step="10"
            value={maxWordPerSent}
            onChange={(e) => setMaxWordPerSent(parseInt(e.target.value))}
          />
        </div>
      </div>
    </div>
  );
}

export default SettingsPanel;
