import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import './styles/theme.css';

function App() {
  const [userId, setUserId] = useState(null);
  const [username, setUsername] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const storedUserId = localStorage.getItem('textor_user_id');
    const storedUsername = localStorage.getItem('textor_user_name');

    if (storedUserId) {
      setUserId(storedUserId);
      setUsername(storedUsername || '');
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = (username) => {
    const normalizedUsername = username.trim();
    const newUserId = `user_${Date.now()}`;

    localStorage.setItem('textor_user_id', newUserId);
    localStorage.setItem('textor_user_name', normalizedUsername);
    setUserId(newUserId);
    setUsername(normalizedUsername);
    setIsLoggedIn(true);
  };

  return (
    <div className="app-container">
      {isLoggedIn ? (
        <ChatInterface userId={userId} username={username} />
      ) : (
        <LoginScreen onLogin={handleLogin} />
      )}
    </div>
  );
}

function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('');
  const canContinue = username.trim().length > 0;

  return (
    <div className="login-container">
      <div className="login-shell">
        <section className="login-aside">
          <span className="section-label">Asistente editorial</span>
          <h1 className="login-title">Textor Predictor Agent</h1>
          <p className="login-subtitle">
            Un espacio más para escribir, recibir sugerencias inteligentes
            y mantener el foco en lo que importa: tu texto.
          </p>

          <div className="login-preview">
            <div className="preview-card">
              <span className="preview-label">Predicción en tiempo real</span>
              <p>
                “La interfaz propone frases y acompaña el
                flujo de escritura sin distraer.”
              </p>
            </div>

            <div className="highlight-grid">
              <div className="highlight-card">
                <span className="highlight-value">Contexto continuo</span>
                <p>Las sugerencias se ajustan a lo que ya vienes redactando.</p>
              </div>
              <div className="highlight-card">
                <span className="highlight-value">Aprendizaje ligero</span>
                <p>El modelo refina la precisión con cada interacción.</p>
              </div>
              <div className="highlight-card">
                <span className="highlight-value">Interfaz impirada en Cloude</span>
                <p>Tonos crema y café para leer y escribir sin fatigar la vista.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="login-card">
          <span className="login-badge">Entrar al espacio</span>
          <h2 className="login-card-title">Comienza una sesión personal</h2>
          <p className="login-card-copy">
            Usa tu nombre para guardar el aprendizaje de las sugerencias y retomar
            tu ritmo cuando vuelvas.
          </p>

          <label className="login-field-label" htmlFor="username">
            Nombre
          </label>
          <input
            id="username"
            type="text"
            placeholder="Tu nombre"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="login-input"
            onKeyDown={(e) => e.key === 'Enter' && canContinue && onLogin(username)}
          />

          <button
            onClick={() => canContinue && onLogin(username)}
            className="login-button"
            disabled={!canContinue}
          >
            Entrar a Textor
          </button>

          <p className="login-footnote">
            Diseñado para una experiencia de escritura más enfocada.
          </p>
        </section>
      </div>
    </div>
  );
}

export default App;
