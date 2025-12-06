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
      console.log('NetSpeech result:', result);
      setNetSpeechResult(result);
    } catch (error) {
      console.error('NetSpeech error:', error);
      setNetSpeechError(error.message);
    } finally {
      setLoadingNetSpeech(false);
    }
  };
  
  const handleSNRAnalysis = async () => {
    if (!selecte