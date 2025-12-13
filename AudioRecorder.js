import React, { useState, useRef, useEffect } from 'react';
import RecordRTC from 'recordrtc';

const BACKEND_NORM_URL = process.env.REACT_APP_BACKEND_NORM_URL;
const BACKEND_GEN_URL = process.env.REACT_APP_BACKEND_GEN_URL;

const AudioRecorder = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [recordedAudioUrl, setRecordedAudioUrl] = useState(null);
    const [apiAudioUrl, setApiAudioUrl] = useState(null);
    const [textInput, setTextInput] = useState('');
    const [recordingTime, setRecordingTime] = useState(0);
    const [isSending, setIsSending] = useState(false); // Thêm state để theo dõi quá trình gửi API
    const recorderRef = useRef(null);
    const streamRef = useRef(null);
    const intervalRef = useRef(null);
    const [sampleRate, setSampleRate] = useState(48000); // Giá trị mặc định
    const [language, setLanguage] = useState('vi'); // Thêm state cho ngôn ngữ

    useEffect(() => {
        const getSampleRate = async () => {
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const maxSampleRate = audioContext.sampleRate; // Lấy sample rate tốt nhất
                setSampleRate(maxSampleRate);
                audioContext.close(); // Đóng context sau khi lấy sample rate
            } catch (error) {
                console.error("Error AudioContext:", error);
            }
        };

        getSampleRate();
    }, []);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: { noiseSuppression: false, echoCancellation: false } });
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
            setRecordingTime(0);

            intervalRef.current = setInterval(() => {
                setRecordingTime(prevTime => prevTime + 1);
            }, 1000);
        } catch (error) {
            console.error("Access to the microphone denied:", error);
        }
    };

    const stopRecording = async () => {
        clearInterval(intervalRef.current);
        recorderRef.current.stopRecording(async () => {
            const audioBlob = recorderRef.current.getBlob();
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.wav');

            try {
                const normResponse = await fetch(BACKEND_NORM_URL, {
                    method: 'POST',
                    body: formData,
                });

                const normResponseBlob = await normResponse.blob();
                const url = URL.createObjectURL(normResponseBlob);
                setRecordedAudioUrl(url);
            } catch (error) {
                console.error('Processing audio has an error:', error);
            }

            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
                streamRef.current = null;
            }
        });
        setIsRecording(false);
        setRecordingTime(0);
    };

    const sendToAPI = async () => {
        if (!recordedAudioUrl || !textInput) {
            alert('Make sure to enter the text and record audio!');
            return;
        }
        console.log('language:', language);

        setApiAudioUrl(null);
        setIsSending(true); // Hiển thị thanh tiến trình
        const audioBlob = recorderRef.current.getBlob();
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav');
        formData.append('gen_text', textInput);
        formData.append('ref_lang', language);

        try {
            const response = await fetch(BACKEND_GEN_URL, {
                method: 'POST',
                body: formData,
            });

            const responseBlob = await response.blob();
            const url = URL.createObjectURL(responseBlob);
            setApiAudioUrl(url);
        } catch (error) {
            console.error('Sending request to API has an error:', error);
        } finally {
            setIsSending(false); // Ẩn thanh tiến trình sau khi nhận kết quả
        }
    };

    const formatTime = (time) => {
        const minutes = Math.floor(time / 60);
        const seconds = time % 60;
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    };

    const getTextForLanguage = () => {
        if (language === 'en') {
            return 'Artificial intelligence is fascinating. it shapes how we learn, create, and innovate.';
        } else if (language === 'vi') {
            // return 'Làng nghề lên số, khởi động với các tọa đàm, các hoạt động chia sẻ, tư vấn và định hướng phát triển, vực dậy các làng nghề, dựa trên sự bùng nổ của kinh doanh online.';
            return 'Namibank xin kính chào qúy khách, Cảm ơn qúy khách đã gọi đến tổng đài chăm sóc khách hàng của ngân hàng Nami, Em có thể hỗ trợ thông tin gì cho quý khách ạ?';
        } else if (language === 'ja') {
            return 'この音声はテキスト読み上げのデモです。音声合成技術によって、自然な発音とイントネーションを再現しています。'; // Bạn có thể thay thế bằng câu phù hợp với ngôn ngữ Nhật
        }
        return '';
    };
    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            height: '100vh',
            backgroundImage: 'url("https://media.istockphoto.com/id/1038737098/vector/glowing-ai-brain-network-vector-illustration.jpg?s=612x612&w=0&k=20&c=Z2vbMCmbKiQzimULCjbhA6OO2z4SZftBh8wr4iTuB7A=")',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            padding: '0 5%',
            boxSizing: 'border-box',
        }}>
            <div style={{
                // position: 'fixed',
                // top: 0,
                // left: 0,
                // right: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-start',
                padding: '1px 1px', // Khoảng cách giữa logo và lề
                width: '100%',
                zIndex: 1000,
                marginBottom: '5%'
            }}>
                <img src="https://www.namitech.io/logo.png" alt="Logo" style={{ width: '100%', maxWidth: '150px', margin: '10px 0' }} />
            </div>
            <div style={{
                width: '100%',
                maxWidth: '600px',
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                borderRadius: '8px',
                padding: '20px',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
                fontFamily: 'Roboto, Arial, sans-serif',
                color: '#333',
            }}>
                <h1 style={{ color: '#4CAF50', fontWeight: 'bold', fontSize: '18px', textAlign: 'center' }}> NamiTech Voice Clone</h1>

                {/* Chọn ngôn ngữ */}
                <div style={{ marginTop: '10px', textAlign: 'left' }}>
                    <h2 style={{
                        fontSize: '14px',
                        color: '#555',
                        display: 'inline-block',
                        marginRight: '20px'
                    }}>Select reference language:</h2>
                    <div style={{ display: 'inline-flex', justifyContent: 'left', gap: '20px', fontSize: '14px'}}>
                        <label>
                            <input
                                type="radio"
                                name="language"
                                value="vi"
                                checked={language === 'vi'}
                                onChange={() => setLanguage('vi')}
                            />
                            Vietnamese
                        </label>
                        <label>
                            <input
                                type="radio"
                                name="language"
                                value="en"
                                checked={language === 'en'}
                                onChange={() => setLanguage('en')}
                            />
                            English
                        </label>
                        <label>
                            <input
                                type="radio"
                                name="language"
                                value="ja"
                                checked={language === 'ja'}
                                onChange={() => setLanguage('ja')}
                            />
                            Japanese
                        </label>
                    </div>
                </div>
                
                <h2 style={{ fontSize: '14px', color: '#555', marginTop: '10px' }}>Read the sentence below in about 8 - 10 seconds to record:</h2>
    
                <p style={{
                    fontSize: '14px',
                    lineHeight: '1.5',
                    padding: '15px',
                    backgroundColor: '#eeeeee',
                    borderRadius: '5px',
                    marginBottom: '20px'
                }}>
                    {getTextForLanguage()}
                </p>
    
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '10px' }}>
                    <button onClick={isRecording ? stopRecording : startRecording} style={{
                        padding: '10px 20px',
                        fontSize: '14px',
                        color: 'white',
                        backgroundColor: isRecording ? '#e74c3c' : '#3498db',
                        border: 'none',
                        borderRadius: '5px',
                        maxWidth: '180px',
                    }}>
                        {isRecording ? 'Stop' : 'Record'}
                    </button>
    
                    {recordedAudioUrl && !isRecording && (
                        <audio src={recordedAudioUrl} controls style={{ marginLeft: '10px', height: '30px' }} />
                    )}
                </div>
    
                {isRecording && (
                    <div style={{ marginTop: '10px', fontSize: '14px', textAlign: 'center' }}>
                        Duration: {formatTime(recordingTime)}
                    </div>
                )}
    
                <div style={{ marginTop: '20px', textAlign: 'left', marginRight:'20px'}}>
                    <label style={{ fontSize: '14px', color: '#555', fontWeight: 'bold'}}>
                        Enter the text:
                    </label>
                    <textarea
                        style={{
                            width: '100%',
                            height: '80px',
                            marginTop: '10px',
                            padding: '10px',
                            fontSize: '14px',
                            lineHeight: '1.5',
                            borderRadius: '5px',
                            border: '1px solid #ccc',
                            resize: 'vertical',
                            fontFamily: 'Roboto, Arial, sans-serif',
                        }}
                        value={textInput}
                        onChange={(e) => setTextInput(e.target.value)}
                    />
                </div>
    
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '20px' }}>
                    <button onClick={sendToAPI} style={{
                        padding: '10px 20px',
                        fontSize: '14px',
                        color: 'white',
                        backgroundColor: '#3498db',
                        border: 'none',
                        borderRadius: '5px',
                        maxWidth: '180px',
                    }}>
                        Generate
                    </button>
    
                    {apiAudioUrl && (
                        <audio src={apiAudioUrl} controls style={{ marginLeft: '10px', height: '30px' }} />
                    )}
                </div>
    
                {isSending && (
                    <div style={{
                        width: '100%',
                        height: '10px',
                        backgroundColor: '#ddd',
                        borderRadius: '5px',
                        overflow: 'hidden',
                        marginTop: '15px'
                    }}>
                        <div style={{
                            width: '100%',
                            height: '100%',
                            backgroundColor: '#27ae60',
                            animation: 'loading 2s linear infinite'
                        }}></div>
                    </div>
                )}
    
                <style>
                    {`
                        @media (max-width: 600px) {
                            h1 { font-size: 16px; }
                            button { max-width: 100%; padding: 8px 16px; }
                            textarea { font-size: 12px; }
                        }
    
                        @keyframes loading {
                            0% { width: 0%; }
                            100% { width: 100%; }
                        }
                    `}
                </style>
            </div>
        </div>
    );
    };
    
    export default AudioRecorder;
