import React from 'react';

export default function InputField({ 
  value, 
  onChange, 
  onSend, 
  placeholder 
}) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="input-container">
      <div className="composer-panel">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="input-field"
          rows="3"
        />

        <div className="composer-footer">
          <p className="composer-hint">Enter para enviar. Shift + Enter para salto de línea.</p>
          <button
            onClick={onSend}
            className="send-button"
            disabled={!value.trim()}
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
}
