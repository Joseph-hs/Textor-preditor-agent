import React, { useState, useRef, useEffect } from 'react';
import InputField from './InputField';
import MessageBubble from './MessageBubble';
import PredictionBox from './PredictionBox';
import { api } from '../services/api';
import '../styles/animations.css';

export default function ChatInterface({ userId, username }) {
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [userStats, setUserStats] = useState(null);
  const messagesEndRef = useRef(null);
  const firstName = username?.trim().split(/\s+/)[0] || 'escritor';
  const wordsLearned = userStats?.words_learned ?? 0;
  const accuracy = userStats ? `${(userStats.accuracy * 100).toFixed(1)}%` : '0.0%';

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    loadUserStats();
  }, [userId]);

  const loadUserStats = async () => {
    try {
      const stats = await api.getUserStats(userId);
      setUserStats(stats);
    } catch (error) {
      console.error('Error cargando estadísticas:', error);
    }
  };

  const handleInputChange = async (value) => {
    setCurrentInput(value);

    if (value.trim().length > 0) {
      await getPredictions(value);
    } else {
      setPredictions([]);
    }
  };

  const getPredictions = async (text) => {
    try {
      setIsLoading(true);
      const response = await api.predict(text, userId);
      setPredictions(response.suggestions.map((word, idx) => ({
        word,
        confidence: response.confidence[idx]
      })));
    } catch (error) {
      console.error('Error obteniendo predicciones:', error);
      setPredictions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPrediction = (word) => {
    const newInput = currentInput + word + ' ';
    setCurrentInput(newInput);

    api.sendFeedback(currentInput, word, userId).catch(console.error);

    setPredictions([]);
    loadUserStats();
  };

  const handleSendMessage = () => {
    if (currentInput.trim()) {
      const newMessage = {
        id: Date.now(),
        text: currentInput,
        sender: 'user',
        timestamp: new Date().toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      };

      setMessages((prev) => [...prev, newMessage]);
      setCurrentInput('');
      setPredictions([]);

      setTimeout(() => {
        const agentMessage = {
          id: Date.now() + 1,
          text: `Procesado: "${newMessage.text}"`,
          sender: 'agent',
          timestamp: new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })
        };
        setMessages(prev => [...prev, agentMessage]);
      }, 500);

      loadUserStats();
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-shell">
        <div className="chat-header">
          <div className="chat-header-main">
            <div className="chat-heading">
              <span className="section-label">Workspace de escritura</span>
              <h1 className="chat-title">Textor Predictor Agent</h1>
              <p className="chat-subtitle">
                Una interfaz más limpia para redactar, completar ideas y dejar que
                las sugerencias trabajen contigo en segundo plano.
              </p>
            </div>

            <div className="chat-header-badge">
              <span className="status-dot" />
              Modelo activo
            </div>
          </div>

          <div className="chat-overview">
            <div className="chat-user-card">
              <span className="chat-user-label">Sesión actual</span>
              <strong>{username || 'Invitado'}</strong>
              <p>
                Hola, {firstName}. Empieza una idea y Textor propondrá el
                siguiente paso.
              </p>
            </div>

            <div className="stats-bar">
              <div className="stat-card">
                <span className="stat-label">Palabras aprendidas</span>
                <strong>{wordsLearned}</strong>
              </div>
              <div className="stat-card">
                <span className="stat-label">Precisión estimada</span>
                <strong>{accuracy}</strong>
              </div>
              <div className="stat-card">
                <span className="stat-label">Sugerencias activas</span>
                <strong>{predictions.length}</strong>
              </div>
            </div>
          </div>
        </div>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-card">
                <span className="empty-state-badge">Listo para escribir</span>
                <h2>
                  Empieza con una frase y deja que Textor complete el ritmo de tu
                  texto.
                </h2>
                <p>
                  Las sugerencias aparecerán debajo del chat a medida que avances,
                  manteniendo una experiencia tranquila y enfocada.
                </p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <PredictionBox
          predictions={predictions}
          onSelectPrediction={handleSelectPrediction}
          isLoading={isLoading}
        />

        <InputField
          value={currentInput}
          onChange={handleInputChange}
          onSend={handleSendMessage}
          placeholder="Escribe una idea, una frase o un párrafo..."
        />
      </div>
    </div>
  );
}
