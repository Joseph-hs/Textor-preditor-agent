import React, { useState, useRef, useEffect } from 'react';
import InputField from './InputField';
import MessageBubble from './MessageBubble';
import PredictionBox from './PredictionBox';
import { api } from '../services/api';
import '../styles/animations.css';

export default function ChatInterface({ userId }) {
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [userStats, setUserStats] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll a los mensajes más nuevos
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Cargar estadísticas del usuario
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
    
    // Registrar feedback
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

      setMessages([...messages, newMessage]);
      setCurrentInput('');
      setPredictions([]);

      // Simular respuesta del agente
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
    <div className="chat-container">
      <div className="chat-header">
        <h1 className="chat-title">Textor Predictor Agent</h1>
        {userStats && (
          <div className="stats-bar">
            <span className="stat-item">
              Palabras aprendidas: <strong>{userStats.words_learned}</strong>
            </span>
            <span className="stat-item">
              Precisión: <strong>{(userStats.accuracy * 100).toFixed(1)}%</strong>
            </span>
          </div>
        )}
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>Bienvenido a Textor Predictor</h2>
            <p>Comienza a escribir y recibe sugerencias inteligentes</p>
          </div>
        ) : (
          messages.map(message => (
            <MessageBubble
              key={message.id}
              message={message}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {predictions.length > 0 && (
        <PredictionBox
          predictions={predictions}
          onSelectPrediction={handleSelectPrediction}
          isLoading={isLoading}
        />
      )}

      <InputField
        value={currentInput}
        onChange={handleInputChange}
        onSend={handleSendMessage}
        placeholder="Escribe aquí..."
      />
    </div>
  );
}