import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import './styles/theme.css';
import './styles/globals.css';

function App() {
  const [userId, setUserId] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Generar o recuperar ID de usuario
    const storedUserId = localStorage.getItem('textor_user_id');
    if (storedUserId) {
      setUserId(storedUserId);
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = (username) => {
    const newUserId = `user_${Date.now()}`;
    localStorage.setItem('textor_user_id', newUserId);
    setUserId(newUserId);
    setIsLoggedIn(true);
  };

  return (
    <div className="app-container">
      {isLoggedIn ? (
        <ChatInterface userId={userId} />
      ) : (
        <LoginScreen onLogin={handleLogin} />
      )}
    </div>
  );
}

function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('');

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">Textor Predictor Agent</h1>
        <p className="login-subtitle">Agente inteligente de predicción de texto</p>
        
        <input
          type="text"
          placeholder="Tu nombre"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="login-input"
          onKeyPress={(e) => e.key === 'Enter' && username && onLogin(username)}
        />
        
        <button
          onClick={() => username && onLogin(username)}
          className="login-button"
        >
          Comenzar
        </button>
      </div>
    </div>
  );
}

export default App;