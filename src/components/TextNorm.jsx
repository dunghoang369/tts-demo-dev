import './TextNorm.css';

function TextNorm({ normalizedText }) {
  return (
    <div className="text-norm-container">
      <div className="text-norm-header">
        <h3 className="text-norm-title">Text Norm (Read-only)</h3>
        <span className="text-norm-info">Normalized text from API</span>
      </div>
      <div className="text-norm-content">
        {normalizedText ? (
          <div className="text-norm-display">{normalizedText}</div>
        ) : (
          <div className="text-norm-placeholder">
            Normalized text will appear here after synthesis...
          </div>
        )}
      </div>
    </div>
  );
}

export default TextNorm;

