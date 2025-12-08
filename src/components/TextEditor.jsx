import { useState, useRef, useEffect } from 'react';
import './TextEditor.css';

function TextEditor({ onSynthesize, isLoading, externalText, onTextChange, showSuggestions = true, readOnly = false }) {
  const [text, setText] = useState('Xin chào, tôi là trợ lý ảo. Hôm nay tôi sẽ giúp bạn chuyển đổi văn bản thành giọng nói tiếng Việt.');
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  // Update text when externalText prop changes
  useEffect(() => {
    if (externalText !== undefined && externalText !== null) {
      setText(externalText);
    }
  }, [externalText]);

  // Notify parent when text changes
  const handleTextChange = (newText) => {
    setText(newText);
    if (onTextChange) {
      onTextChange(newText);
    }
  };

  const handleSpeak = async () => {
    if (!text.trim()) {
      alert('Vui lòng nhập văn bản để chuyển đổi thành giọng nói');
      return;
    }
    
    const audioUrl = await onSynthesize(text);
    if (audioUrl && audioRef.current) {
      audioRef.current.src = audioUrl;
      audioRef.current.play();
      setIsPlaying(true);
      setIsPaused(false);
    }
  };

  const handlePause = () => {
    if (audioRef.current && !audioRef.current.paused) {
      audioRef.current.pause();
      setIsPaused(true);
    }
  };

  const handleResume = () => {
    if (audioRef.current && audioRef.current.paused) {
      audioRef.current.play();
      setIsPaused(false);
    }
  };

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      setIsPaused(false);
    }
  };

  const handleClear = () => {
    handleTextChange('');
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
    setIsPaused(false);
  };

  const quickStartExamples = [
    {
      icon: '📖',
      label: 'Kể lại một câu chuyện',
      text: "Anh đã nói rằng sẽ luôn ở bên em. Nhưng khi mọi thứ sụp đổ, khi em quay lại tìm kiếm một bờ vai… anh ở đâu? Thành phố này đã nghiền nát em, còn anh chỉ đứng nhìn, nhấm nháp ly latte nửa cà phê nửa sữa của mình."
    },
    {
      icon: '😄',
      label: 'kể lại một câu chuyện cười',
      text: "Tại sao các nhà khoa học không tin vào nguyên tử? Vì chúng tạo ra mọi thứ! Và nói về việc tạo ra mọi thứ, có bạn đã nghe về nhà toán học đang sợ các số âm chưa? Anh ấy sẽ dừng lại ở bất cứ điều gì để tránh chúng!"
    },
    {
      icon: '🎙️',
      label: 'Đọc một đoạn quảng cáo',
      text: "Đây là điện thoại thông minh mới nhất - SmartPhone Pro Max Ultra - nơi sự sáng tạo gặp điểm với sự hoàn hảo. Với màn hình sắc nét và hiển thị rõ ràng, hiệu suất nhanh chóng và camera chụp ảnh với độ phân giải cao, có sẵn ngay tại cửa hàng gần nhất của bạn."
    },
    {
      icon: '🌍',
      label: 'Nói bằng các ngôn ngữ khác nhau',
      text: "Xin chào, tôi là Rachel. Bonjour, je m'appelle Rachel. Hola, me llamo Rachel. Ciao, mi chiamo Rachel. こんにちは、私の名前はレイチェルです。"
    },
    {
      icon: '🎬',
      label: 'Đọc lời thoại trong một đoạn phim điện ảnh',
      text: "Cơn mưa trút xuống như những giọt lệ từ thiên đường, khi cô đứng ở mép bến tàu, nhìn chằm chằm vào màn đêm. “Em chưa bao giờ muốn mọi chuyện kết thúc như thế này,” cô thì thầm, giọng nghẹn lại. Nhưng đại dương vẫn giữ kín những bí mật của nó — lặng im và lạnh lùng."
    },
    {
      icon: '🧘',
      label: 'Hướng dẫn một lớp tập thể dục',
      text: "Hít vào sâu... và thở ra từ từ. Cảm nhận sự thoải mái rời khỏi cơ thể với mỗi hít ra. Bạn yên tĩnh. Bạn ở giữa. Bạn yên bình. Để tâm trí bay nhẹ như lá bèo trên hồ yên lặng."
    }
  ];

  const handleQuickStart = (exampleText) => {
    handleTextChange(exampleText);
  };

  return (
    <div className="text-editor">
      <textarea
        className="text-input"
        value={text}
        onChange={(e) => handleTextChange(e.target.value)}
        placeholder="Type or paste text to synthesize..."
        disabled={isLoading}
        readOnly={readOnly}
      />
      
      {!text.trim() && showSuggestions && (
        <div className="quick-start">
          <p className="quick-start-title">Get started with</p>
          <div className="quick-start-buttons">
            {quickStartExamples.map((example, index) => (
              <button
                key={index}
                className="quick-start-btn"
                onClick={() => handleQuickStart(example.text)}
                disabled={isLoading}
              >
                <span className="quick-start-icon">{example.icon}</span>
                <span className="quick-start-label">{example.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}
      
      <div className="controls">
        <div className="controls-left">
          <button 
            className="btn btn-primary" 
            onClick={handleSpeak}
            disabled={isLoading || !text.trim()}
          >
            {isLoading ? '⏳ Generating...' : '▶︎ Speak'}
          </button>
          <button 
            className="btn btn-ghost" 
            onClick={handlePause}
            disabled={!isPlaying || isPaused}
          >
            ⏸ Pause
          </button>
          <button 
            className="btn btn-ghost" 
            onClick={handleResume}
            disabled={!isPaused}
          >
            ⏵ Resume
          </button>
          <button 
            className="btn btn-ghost" 
            onClick={handleStop}
            disabled={!isPlaying && !isPaused}
          >
            ⏹ Stop
          </button>
        </div>
        
        <div className="controls-right">
          <button 
            className="btn btn-ghost" 
            onClick={handleClear}
            title="Clear text"
            disabled={readOnly}
          >
            ✕ Clear
          </button>
        </div>
      </div>

      <audio
        ref={audioRef}
        className="audio-player"
        controls
        onEnded={handleAudioEnded}
      />
    </div>
  );
}

export default TextEditor;

