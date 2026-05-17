import React from 'react';

export default function MessageBubble({ message }) {
  const isUser = message.sender === 'user';
  const author = isUser ? 'Tú' : 'Textor';

  return (
    <div className={`message-row ${isUser ? 'user' : 'agent'}`}>
      <div className={`message-bubble ${isUser ? 'user' : 'agent'}`}>
        <span className="message-author">{author}</span>
        <div className="message-content">
          <p>{message.text}</p>
        </div>
        <span className="message-time">{message.timestamp}</span>
      </div>
    </div>
  );
}
