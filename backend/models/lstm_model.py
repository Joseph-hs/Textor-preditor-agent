import numpy as np
import tensorflow as tf
from tensorflow import keras
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class LSTMModel:
    def __init__(self, vocab_size: int = 500, embedding_dim: int = 128, lstm_units: int = 256):
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.lstm_units = lstm_units
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.model = None
        self.is_trained = False
    
    def train(self, words: List[str], epochs: int = 3):
        unique_words = sorted(set(words))
        self.word_to_idx = {word: idx for idx, word in enumerate(unique_words)}
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}
        sequences = []
        for i in range(len(words) - 1):
            if words[i] in self.word_to_idx:
                sequences.append([self.word_to_idx[words[i]], self.word_to_idx.get(words[i + 1], 0)])
        if not sequences:
            logger.warning("No hay suficientes secuencias para entrenar LSTM")
            return
        X = np.array([seq[0] for seq in sequences]).reshape(-1, 1)
        y = tf.keras.utils.to_categorical([seq[1] for seq in sequences], num_classes=len(self.word_to_idx))
        self.model = keras.Sequential([
            keras.layers.Embedding(input_dim=len(self.word_to_idx), output_dim=self.embedding_dim, input_length=1),
            keras.layers.LSTM(self.lstm_units, return_sequences=False),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(len(self.word_to_idx), activation='softmax')
        ])
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        self.model.fit(X, y, epochs=epochs, batch_size=32, verbose=0, validation_split=0.2)
        self.is_trained = True
        logger.info(f"LSTM entrenado: {len(self.word_to_idx)} palabras")
    
    def predict_next(self, context: List[str], k: int = 5) -> List[Tuple[str, float]]:
        if not self.is_trained or self.model is None:
            return []
        try:
            last_word = context[-1] if context else None
            if not last_word or last_word not in self.word_to_idx:
                return []
            word_idx = self.word_to_idx[last_word]
            input_data = np.array([[word_idx]])
            predictions = self.model.predict(input_data, verbose=0)[0]
            top_k_indices = np.argsort(predictions)[-k:][::-1]
            results = []
            for idx in top_k_indices:
                if idx in self.idx_to_word:
                    word = self.idx_to_word[idx]
                    confidence = float(predictions[idx])
                    if confidence > 0.01:
                        results.append((word, confidence))
            return results
        except Exception as e:
            logger.error(f"Error en prediccion LSTM: {str(e)}")
            return []