// Audio API Service - handles audio file uploads to various audio processing APIs

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/**
 * Send audio file to NetSpeech API for quality analysis
 * @param {File} file - Audio file to analyze
 * @returns {Promise<Object>} - NetSpeech analysis results
 */
export const sendToNetSpeech = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/audio/netspeech`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'NetSpeech API request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('NetSpeech API error:', error);
    throw error;
  }
};

/**
 * Send audio file to SNR API for signal-to-noise ratio analysis
 * @param {File} file - Audio file to analyze
 * @returns {Promise<Object>} - SNR analysis results
 */
export const sendToSNR = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/audio/snr`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'SNR API request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('SNR API error:', error);
    throw error;
  }
};

/**
 * Send audio file to Audio Converter API with conversion parameters
 * @param {File} file - Audio file to convert
 * @param {Object} params - Conversion parameters
 * @param {number} params.sample_rate - Sample rate (default: 22050)
 * @param {number} params.rate - Playback rate (default: 1.0)
 * @param {string} params.return_type - Return type: 'url' or 'base64' (default: 'url')
 * @param {string} params.audio_format - Audio format: 'wav' or 'mp3' (default: 'wav')
 * @returns {Promise<Object>} - Converted audio results
 */
export const sendToConverter = async (file, params = {}) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    // Build query parameters
    const queryParams = new URLSearchParams({
      sample_rate: params.sample_rate || 22050,
      rate: params.rate || 1.0,
      return_type: params.return_type || 'url',
      audio_format: params.audio_format || 'wav',
    });

    const response = await fetch(
      `${API_BASE_URL}/api/audio/converter?${queryParams}`,
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Audio Converter API request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Audio Converter API error:', error);
    throw error;
  }
};

