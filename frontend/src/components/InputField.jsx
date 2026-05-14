import React from 'react';

export default function InputField({ 
  value, 
  onChange, 
  onSend, 
  placeholder 
}) {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="input-container">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        className="input-field"
        rows="3"
      />
      <button
        onClick={onSend}
        className="send-button"
        disabled={!value.trim()}
      >
        Enviar
      </button>
    </div>
  );
}