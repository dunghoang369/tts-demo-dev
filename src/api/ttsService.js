// Vietnamese TTS API Service
// Integrated with http://115.79.192.192:19977/invocations

/**
 * Synthesizes speech from text using the specified voice, model, rate, return type, audio format, and max words per sentence
 * @param {string} text - The text to convert to speech
 * @param {string} voice - The voice ID to use
 * @param {string} model - The model ID to use
 * @param {string} rate - The speed of the speech
 * @param {string} returnType - The return type (url or file)
 * @param {string} audioFormat - The audio format (wav or mp3)
 * @param {number} maxWordPerSent - Maximum words per sentence
 * @returns {Promise<{audioUrl: string, blob: Blob, normalizedText: string}>} - Audio URL, blob, and normalized text
 */
export async function synthesize(text, voice, model, rate, returnType, audioFormat, maxWordPerSent) {
  console.log('TTS API called with:', { text, voice, model, rate, returnType, audioFormat, maxWordPerSent });
  
  // Use backend proxy instead of calling external API directly
  const API_URL = '/api/tts/synthesize';
  
  // Build JSON body for the TTS API
  const requestBody = {
    content: text,
    rate: parseFloat(rate) || 1.0,
    sample_rate: parseInt(model) || 16000,
    accent: parseInt(voice) || 4,
    return_type: returnType || 'url',
    audio_format: audioFormat || 'wav',
    max_word_per_sent: parseInt(maxWordPerSent) || 100
  };
  
  console.log('Request body:', requestBody);
  
  try {
    // Call backend proxy with POST
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', response.status, errorText);
      throw new Error(`TTS API failed: ${response.status} - ${errorText}`);
    }
    
    // Handle different return types
    if (returnType === 'url') {
      // API returns JSON with base64-encoded waveform
      const data = await response.json();
      console.log('API Response status:', data.status, data.description);
      console.log('Full API Response:', data);
      console.log('Available keys:', Object.keys(data));
      
      // Extract the base64 waveform from the response
      const base64Waveform = data.audio;
      const normalizedText = data.normed_text || '';
      
      console.log('Extracted normalizedText:', normalizedText);
      
      if (!base64Waveform) {
        console.error('Response data:', data);
        throw new Error('No waveform data in response');
      }
      
      // Convert base64 to binary
      const binaryString = atob(base64Waveform);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Create blob from binary data
      const blob = new Blob([bytes], { type: `audio/${audioFormat}` });
      const audioUrl = URL.createObjectURL(blob);
      return { audioUrl, blob, normalizedText };
    } else {
      // return_type is 'file' - returns audio blob directly
      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      return { audioUrl, blob, normalizedText: '' };
    }
  } catch (error) {
    console.error('Synthesis error:', error);
    throw error;
  }
}

/**
 * Fetch available speech rates (speeds)
 * @returns {Promise<Array<{id: string, name: string}>>}
 */
export async function getRates() {
  console.log('getRates API called');
  
  // Return available speech rates for the TTS API
  return [
    { id: '0.8', name: '0.8x (Very Slow)' },
    { id: '0.9', name: '0.9x (Slow)' },
    { id: '1.0', name: '1.0x (Normal)' },
    { id: '1.05', name: '1.05x (Slightly Fast)' },
    { id: '1.1', name: '1.1x (Fast)' },
    { id: '1.2', name: '1.2x (Very Fast)' },
  ];
}

/**
 * Fetch available voices from the backend
 * @returns {Promise<Array<{id: string, name: string}>>}
 */
export async function getVoices() {
  console.log('getVoices API called');
  
  // Return Vietnamese voices available from the TTS API
  return [
    { id: '1', name: 'Hannah (Nữ miền Nam - Vi - Chất lượng thấp)' },
    { id: '2', name: 'Thu Thuỷ (Nữ miền Bắc - Vi - Chất lượng thấp)' },
    { id: '3', name: 'Kim Chi (Nữ miền Bắc - Vi)' },
    { id: '4', name: 'Hồng Phượng (Nữ miền Bắc - Vi)' },
    { id: '5', name: 'Phương Anh (Nữ miền Nam - Vi)' },
    { id: '6', name: 'Sơn Long (Nam miền bắc - Vi)' },
    { id: '7', name: 'Cẩm Tú (Nữ miền Trung - Vi)' },
    { id: '8', name: 'Hồng Phúc (Nam miền Nam - Vi)' },
    { id: '9', name: 'LJSpeech (Nữ - En - Thử nghiệm)' },
    { id: '10', name: 'Ngọc Bích (Nữ miền Bắc - Vi)' }
  ];
}

/**
 * Fetch available models (sample rates) from the backend
 * @returns {Promise<Array<{id: string, name: string}>>}
 */
export async function getModels() {
  console.log('getModels API called');
  
  // Return available sample rates for the TTS API
  return [
    { id: '8000', name: '8kHz (Low Quality)' },
    { id: '16000', name: '16kHz (Standard)' },
    { id: '22050', name: '22kHz (High Quality)' },
    { id: '44100', name: '44kHz (Premium)' }
  ];
}

/**
 * Fetch available return types
 * @returns {Promise<Array<{id: string, name: string}>>}
 */
export async function getReturnTypes() {
  console.log('getReturnTypes API called');
  
  // Return available return types for the TTS API
  return [
    { id: 'url', name: 'URL' },
    { id: 'file', name: 'File' }
  ];
}

/**
 * Fetch available audio formats
 * @returns {Promise<Array<{id: string, name: string}>>}
 */
export async function getAudioFormats() {
  console.log('getAudioFormats API called');
  
  // Return available audio formats for the TTS API
  return [
    { id: 'wav', name: 'WAV' },
    { id: 'mp3', name: 'MP3' }
  ];
}
