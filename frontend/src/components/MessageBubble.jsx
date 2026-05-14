import React from 'react';

export default function MessageBubble({ message }) {
  const isUser = message.sender === 'user';

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'agent'}`}>
      <div className="message-content">
        <p>{message.text}</p>
      </div>
      <span className="message-time">{message.timestamp}</span>
    </div>
  );
}