import React from 'react';

export default function PredictionBox({
  predictions,
  onSelectPrediction,
  isLoading
}) {
  if (predictions.length === 0 && !isLoading) {
    return null;
  }

  return (
    <div className="prediction-box">
      <div className="prediction-header">
        <p className="prediction-label">
          {isLoading ? 'Analizando el contexto...' : 'Sugerencias disponibles'}
        </p>
        {!isLoading && (
          <span className="prediction-count">{predictions.length} opciones</span>
        )}
      </div>
      <div className="prediction-list">
        {predictions.map((pred, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrediction(pred.word)}
            className="prediction-button"
            title={`Confianza: ${(pred.confidence * 100).toFixed(1)}%`}
          >
            <span className="pred-word">{pred.word}</span>
            <span className="pred-confidence">
              {(pred.confidence * 100).toFixed(0)}%
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
